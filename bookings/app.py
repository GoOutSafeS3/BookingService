from logging import debug
import connexion
import datetime
import logging
import configparser
import sys
import os
import dateutil.parser

from flask import current_app

from connexion import NoContent, request

from bookings.orm import db, Booking

from bookings.utils import add_booking, get_a_table, update_booking, put_fake_data

from bookings.errors import Error, Error400, Error404, Error500

import sys
sys.path.append("./bookings/")

"""
The default app configuration: 
in case a configuration is not found or 
some data is missing
"""
DEFAULT_CONFIGURATION = { 

    "FAKE_DATA": False, # insert some default data in the database (for tests)
    "REMOVE_DB": False, # remove database file when the app starts
    "DB_DROPALL": False,

    "IP": "0.0.0.0", # the app ip
    "PORT": 8080, # the app port
    "DEBUG":True, # set debug mode

    "SQLALCHEMY_DATABASE_URI": "bookings.db", # the database path/name
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "USE_MOCKS": False, # use mocks for external calls
    "TIMEOUT": 2, # timeout for external calls
    "REST_SERVICE_URL": "http://restaurants:8080/", # restaurant microservice url

}

def get_bookings(user=None, rest=None, table=None, begin=None, end=None, begin_entrance=None, end_entrance=None):
    """ Return the list of bookings.

    GET /bookings?[user=U_ID&][rest=R_ID&][table=T_ID&][begin=BEGING_DT&][end=END_DT&][begin_entrance=BEGING_ENT_DT&][end_entrance=END_ENT_DT&]

    It's possible to filter the bookings thanks the query's parameters.
    The parameters can be overlapped in any way.
    All paramters are optional.

    - user: All the booking of a specific user (by id)
    - rest: All the booking of a specific restaurant (by id)
    - table: All the booking of a specific table (by id)
    - begin: All bookings from a certain date onwards (datetime ISO 8601 - Chapter 5.6)
    - end: All bookings up to a certain date onwards (datetime ISO 8601 - Chapter 5.6)
    - begin_entrance: All bookings from a certain entrance date onwards (datetime ISO 8601 - Chapter 5.6)
    - end_entrance: All bookings up to a certain entrance date onwards (datetime ISO 8601 - Chapter 5.6)

    If begin and not end is specified, all those starting from begin are taken. Same thing for end.

    Status Codes:
        200 - OK
        400 - Wrong datetime format
    """

    q = db.session.query(Booking)
    
    if user is not None:
        q = q.filter_by(user_id=user)

    if rest is not None:
        q = q.filter_by(restaurant_id=rest)

    if table is not None:
        q = q.filter_by(table_id=table)

    if begin is not None:
        try:
            begin = dateutil.parser.parse(begin)
        except:
            return Error400("Begin Arguments is not a valid datetime").get()
        q = q.filter(Booking.booking_datetime >= begin)

    if end is not None:
        try:
            end = dateutil.parser.parse(end)
        except:
            return Error400("End Arguments is not a valid datetime").get()
        q = q.filter(Booking.booking_datetime <= end)

    if begin_entrance is not None:
        try:
            begin_entrance = dateutil.parser.parse(begin_entrance)
        except:
            return Error400("begin_entrance Arguments is not a valid datetime").get()
        q = q.filter(Booking.entrance_datetime >= begin_entrance)

    if end_entrance is not None:
        try:
            end_entrance = dateutil.parser.parse(end_entrance)
        except:
            return Error400("end_entrance Arguments is not a valid datetime").get()
        q = q.filter(Booking.entrance_datetime <= end_entrance)

    return [p.dump() for p in q], 200

def new_booking():
    """ Add a new booking.

    POST /bookings
    
    Returns the booking if it can be made, otherwise returns an error message.

    Requires a json object with:
        - number_of_people: the number of people for the booking
        - booking_datetime: the datetime of the booking
        - user_id: the id of the user who made the booking
        - restaurant_id: the id of the restaurant

    Status Codes:
        201 - The booking has been created
        400 - Wrong datetime
        409 - Impossible to change the booking (it is full, it is closed ...)
        500 - Error in communicating with the restaurant service or problem with the database (try again)
    """

    req = request.json
    try:
        req["booking_datetime"] = dateutil.parser.parse(req["booking_datetime"])
    except:
        return Error400("booking_datetime is not a valid datetime").get()

    timezone = req["booking_datetime"].tzinfo
    now = datetime.datetime.now(timezone) #timezone aware computation
    if req["booking_datetime"] <= now:
        return Error400("booking_datetime must be in the future").get()

    # try to get a table in the restaurant for the booking
    table = get_a_table(req["restaurant_id"],req["number_of_people"],req["booking_datetime"])
    if table is None: # an error occured (problem during the connection with the restaurant's microservice)
        return Error500().get()
    elif table == -1: # The restaurant does not accept the booking because there are no free tables
        return Error("about:blank","Conflict",409,"We are sorry! It is not possible to make the booking: there are no free tables!").get()
    elif table == -2: # The restaurant does not accept the booking because it is closed
        return Error("about:blank","Conflict",409,"We are sorry! It is not possible to make the booking: the restaurant is closed on that datetime!").get()

    booking = add_booking(req["user_id"],req["restaurant_id"],req["number_of_people"],req["booking_datetime"],table)
    if booking is None: # DB error
        return Error500().get()
    
    booking, status_code = get_booking(booking)
    if status_code == 200:
        return booking, 201
    else: # unexpected error
        return Error500().get()
    

def get_booking(booking_id):
    """ Return a specific booking (request by id)

    GET /bookings/{booking_id}

        Status Codes:
            200 - OK
            404 - Booking not found
    """
    q = db.session.query(Booking).filter_by(id = booking_id).first()
    if q is None:
        return Error404("Booking not found").get()
    return q.dump(), 200

def put_booking(booking_id, entrance=False):
    """ Edit a booking.

    GET /bookings/{booking_id}?[entrance=true/false]

    Changes the number of people and/or the date of the booking. 
    Or marks the user's entry.

    The request to mark the entrance is made through the query parameter entrance (a boolean)

    Change requests are made through json objects with the following properties (both optional)
        - booking_datetime: the new requested datetime
        - number_of_people: the new requested number of people

    If one of the two fields is not set, the one already entered is recovered.
    If both are not entered the request is void (unless required to mark the entry()in this case the json is ignored).

    If entry is marked, other requests for changes are ignored (if the user has already entered the changes no longer make sense).
    Likewise, if the entry is marked, no more changes can be made.

    The booking must not have already passed, in the event of a change.

    Change of a booking may not always be possible (on the requested date there are no seats available, the restaurant is closed on that date ...)

    Status Codes:
        200 - OK
        400 - Wrong datetime or bad request (entry already marked)
        404 - Booking not found
        409 - Impossible to change the booking
        500 - Error in communicating with the restaurant service or problem with the database (try again)
    """
    q = db.session.query(Booking).filter_by(id = booking_id).first()
    if q is None:
        return Error404("Booking not found").get()
    q = q.dump()

    if entrance:
        if q["entrance_datetime"] is not None:
            return Error400("Entrance has already been marked for this booking").get()
        now = datetime.datetime.now()
        booking = update_booking(q["id"],q["number_of_people"],q["booking_datetime"],q["table_id"],now)
        if booking is None: # DB error
            return Error500().get()
        booking, status_code = get_booking(booking)
        if status_code == 200: 
            return booking, 200
        else: # unexpected error
            return Error500().get()

    if q["entrance_datetime"] is not None:
        return Error400("The entry has already been marked, the reservation can no longer be changed").get()

    now = datetime.datetime.now()
    if q["booking_datetime"] < now:
        return Error400("You cannot change a past booking").get()

    req = request.json

    if "booking_datetime" in req and req["booking_datetime"] is not None:
        try:
            req["booking_datetime"] = dateutil.parser.parse(req["booking_datetime"])
        except:
            return Error400("booking_datetime is not a valid datetime").get()
        timezone = req["booking_datetime"].tzinfo
        now = datetime.datetime.now(timezone)
        if req["booking_datetime"] <= now:
            return Error400("booking_datetime must be in the future").get()
    else: # use the "old" datetime
        req["booking_datetime"] = q["booking_datetime"]

    if "number_of_people" not in req or req["number_of_people"] is None:
        req["number_of_people"] = q["number_of_people"]

    if (q["booking_datetime"] != req["booking_datetime"]) or (q["number_of_people"] != req["number_of_people"]):
        
        table = get_a_table(q["restaurant_id"],req["number_of_people"],req["booking_datetime"],excluded=booking_id) # try to get a table
        
        if table is None: # an error occured (problem during the connection with the restaurant's microservice)
            return Error500().get()
        elif table == -1: # The restaurant does not accept the changes because there are no free tables
            return Error("about:blank","Conflict",409,"We are sorry! It is not possible to change the booking: there are no free tables!").get()
        elif table == -2: # The restaurant does not accept the changes because it is closed
            return Error("about:blank","Conflict",409,"We are sorry! It is not possible to change the booking: the restaurant is closed on that datetime!").get()

        booking = update_booking(q["id"],req["number_of_people"],req["booking_datetime"],table)
        if booking is None: # DB error
            return Error500().get()
        
        booking, status_code = get_booking(booking)
        if status_code == 200:
            return booking, 200
        else: # unexpected error
            return Error500().get()
    
    return Error400("No changes were requested").get()


def delete_booking(booking_id):
    """ Delete a booking specified by the id.

    DELETE /bookings/{booking_id}
    
    Deletion is only possible if the booking has not yet passed.

    Otherwise it remains stored (necessary for contact tracing)

    Status Codes:
        204 - Deleted
        404 - Booking not found
        403 - The booking cannot be deleted: it is a past reservation
        500 - Error with the database
    """
    q = db.session.query(Booking).filter_by(id = booking_id)
    p = q.first()
    if p is None:
        return Error404("Booking not found").get()

    p = p.dump()
    
    now = datetime.datetime.now()

    if p["booking_datetime"] <= now:
        return Error("about:blank","Unacceptable Request",403,"The request cannot be accepted: past bookings cannot be deleted").get()

    try:
        q.delete()
        db.session.commit()
        return NoContent, 204
    except Exception as e: # DB error
        db.session.rollback()
        logging.info("- GoOutSafe:Bookings IMPOSSIBLE TO DELETE %s -> %s",str(p["id"]),e)
        return Error500().get() # DB error

def get_config(configuration=None):
    """ Returns a json file containing the configuration to use in the app

    The configuration to be used can be passed as a parameter, 
    otherwise the one indicated by default in config.ini is chosen

    ------------------------------------
    [CONFIG]
    CONFIG = The_default_configuration
    ------------------------------------

    Params:
        - configuration: if it is a string it indicates the configuration to choose in config.ini
    """
    try:
        parser = configparser.ConfigParser()
        if parser.read('config.ini') != []:
            
            if type(configuration) != str: # if it's not a string, take the default one
                configuration = parser["CONFIG"]["CONFIG"]

            logging.info("- GoOutSafe:Bookings CONFIGURATION: %s",configuration)
            configuration = parser._sections[configuration] # get the configuration data

            parsed_configuration = {}
            for k,v in configuration.items(): # Capitalize keys and translate strings (when possible) to their relative number or boolean
                k = k.upper()
                parsed_configuration[k] = v
                try:
                    parsed_configuration[k] = int(v)
                except:
                    try:
                        parsed_configuration[k] = float(v)
                    except:
                        if v == "true":
                            parsed_configuration[k] = True
                        elif v == "false":
                            parsed_configuration[k] = False

            for k,v in DEFAULT_CONFIGURATION.items():
                if not k in parsed_configuration: # if some data are missing enter the default ones
                    parsed_configuration[k] = v

            return parsed_configuration
        else:
            return DEFAULT_CONFIGURATION
    except Exception as e:
        logging.info("- GoOutSafe:Bookings CONFIGURATION ERROR: %s",e)
        logging.info("- GoOutSafe:Bookings RUNNING: Default Configuration")
        return DEFAULT_CONFIGURATION

def setup(application, config):

    if config["REMOVE_DB"]: # remove the db file
        logging.info("- GoOutSafe:Bookings Removing Database...")
        try:
            os.remove("bookings/"+config["SQLALCHEMY_DATABASE_URI"])
            logging.info("- GoOutSafe:Bookings Database Removed")
        except:
            pass

    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+config["SQLALCHEMY_DATABASE_URI"]

    for k,v in config.items():
        application.config[k] = v # insert the requested configuration in the app configuration

    db.init_app(application)

    if config["DB_DROPALL"]: #remove the data in the db
        logging.info("- GoOutSafe:Bookings Dropping All from Database...")
        db.drop_all(app=application)

    db.create_all(app=application)

    if config["FAKE_DATA"]: #add fake data (for testing)
        logging.info("- GoOutSafe:Bookings Adding Fake Data...")
        with application.app_context():
            put_fake_data()

def create_app(configuration=None):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('./swagger.yaml')
    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app

    conf = get_config(configuration)
    logging.info(conf)
    logging.info("- GoOutSafe:Bookings ONLINE @ ("+conf["IP"]+":"+str(conf["PORT"])+")")
    with app.app.app_context():
        setup(application, conf)

    return app

if __name__ == '__main__':

    c = None
    if len(sys.argv) > 1: # if it is inserted
        c = sys.argv[1] # get the configuration name from the arguments

    app = create_app(c)

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"], 
            port=current_app.config["PORT"], 
            debug=current_app.config["DEBUG"]
            )
