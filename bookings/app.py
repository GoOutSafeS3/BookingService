from datetime import date
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

"""
The default app configuration: 
in case a configuration is not found or 
some data is missing
"""
DEFAULT_CONFIGURATION = { 

    "FAKE_DATA": False, # insert some default data in the database (for tests)
    "REMOVE_DB": False, # remove database file when the app starts
    "DB_DROPALL": False,

    "IP": "127.0.0.1", # the app ip
    "PORT": 8080, # the app port
    "DEBUG":True, # set debug mode

    "SQLALCHEMY_DATABASE_URI": "bookings.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "USE_MOCKS": False,

}

# --- TO DO ---
# CHECK TIMEZONES (?)
# CONTACTS

def get_bookings(user=None, rest=None, table=None, begin=None, end=None):

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
            return Error400("begin","Begin Arguments is not a valid datetime").get()
        q = q.filter(Booking.booking_datetime >= begin)
    if end is not None:
        try:
            end = dateutil.parser.parse(end)
        except:
            return Error400("end","End Arguments is not a valid datetime").get()
        q = q.filter(Booking.booking_datetime <= end)

    return [p.dump() for p in q], 200

def new_booking():

    req = request.json
    try:
        req["booking_datetime"] = dateutil.parser.parse(req["booking_datetime"])
    except:
        return Error400("booking_datetime","booking_datetime is not a valid datetime").get()

    timezone = req["booking_datetime"].tzinfo
    now = datetime.datetime.now(timezone)
    if req["booking_datetime"] <= now:
        return Error400("booking_datetime","booking_datetime must be in the future").get()

    table = get_a_table(req["restaurant_id"],req["number_of_people"],req["booking_datetime"])
    if table is None:
        return Error500().get()
    elif table == -1:
        return Error400("booking","It is not possible to make the booking").get()

    booking = add_booking(req["user_id"],req["restaurant_id"],req["number_of_people"],req["booking_datetime"],table)
    if booking is None:
        return Error500().get()
    
    booking, status_code = get_booking(booking)
    if status_code == 200:
        return booking, 200
    else:
        return Error500().get()
    

def get_booking(booking_id):
    q = db.session.query(Booking).filter_by(id = booking_id).first()
    if q is None:
        return Error404("booking_id","Booking not found").get()
    return q.dump(), 200

def put_booking(booking_id, entrance=False):
    q = db.session.query(Booking).filter_by(id = booking_id).first()
    if q is None:
        return Error404("booking_id","Booking not found").get()
    q = q.dump()

    if entrance:
        if q["entrance_datetime"] is not None:
            return Error400("entrance","Entrance has already been marked for this booking").get()
        now = datetime.datetime.now()
        booking = update_booking(q["id"],q["number_of_people"],q["booking_datetime"],q["table_id"],now)
        if booking is None:
            return Error500().get()
        booking, status_code = get_booking(booking)
        if status_code == 200:
            return booking, 200
        else:
            return Error500().get()

    req = request.json

    if "booking_datetime" in req:
        try:
            req["booking_datetime"] = dateutil.parser.parse(req["booking_datetime"])
        except:
            return Error400("booking_datetime","booking_datetime is not a valid datetime").get()
        timezone = req["booking_datetime"].tzinfo
        now = datetime.datetime.now(timezone)
        if req["booking_datetime"] <= now:
            return Error400("booking_datetime","booking_datetime must be in the future").get()
    else:
        req["booking_datetime"] = q["booking_datetime"]

    if "number_of_people" not in req:
        req["number_of_people"] = q["number_of_people"]

    if (q["booking_datetime"] != req["booking_datetime"]) or (q["number_of_people"] != req["number_of_people"]):
        
        table = get_a_table(q["restaurant_id"],req["number_of_people"],req["booking_datetime"])
        if table is None:
            return Error500().get()
        elif table == -1:
            return Error400("booking","It is not possible to make the booking").get()

        booking = update_booking(q["id"],req["number_of_people"],req["booking_datetime"],table)
        if booking is None:
            return Error500().get()
        
        booking, status_code = get_booking(booking)
        if status_code == 200:
            return booking, 200
        else:
            return Error500().get()
    
    return Error400("booking","No changes were requested").get()


def delete_booking(booking_id):
    q = db.session.query(Booking).filter_by(id = booking_id)
    p = q.first()
    if p is None:
        return Error404("booking_id","Booking not found").get()

    p = p.dump()
    
    now = datetime.datetime.now()

    if p["booking_datetime"] <= now:
        return Error("wrongrequest","Wrong Request",403,"The request cannot be accepted: past bookings cannot be deleted").get()

    try:
        q.delete()
        db.session.commit()
        return NoContent, 204
    except Exception as e:
        logging.info("- GoOutSafe:Bookings IMPOSSIBLE TO DELETE %s -> %s",str(p["id"]),e)
        return Error500().get()

def get_contacts(user_id): #TODO
    return Error404("user_id","User not found").get()

def get_config(configuration=None):
    """
    returns a json file containing the configuration to use in the app

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
            for k,v in configuration.items():
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

    if config["REMOVE_DB"]:
        logging.info("- GoOutSafe:Bookings Removing Database...")
        try:
            os.remove("bookings/"+config["SQLALCHEMY_DATABASE_URI"])
            logging.info("- GoOutSafe:Bookings Database Removed")
        except:
            pass

    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+config["SQLALCHEMY_DATABASE_URI"]

    for k,v in config.items():
        application.config[k] = v

    db.init_app(application)

    if config["DB_DROPALL"]:
        logging.info("- GoOutSafe:Bookings Dropping All from Database...")
        db.drop_all(app=application)

    db.create_all(app=application)

    if config["FAKE_DATA"]:
        logging.info("- GoOutSafe:Bookings Adding Fake Data...")
        with application.app_context():
            put_fake_data()

def create_app(configuration=None):
    logging.basicConfig(level=logging.INFO)

    app = connexion.App(__name__)
    app.add_api('swagger.yaml')
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
    if len(sys.argv) > 1:
        c = sys.argv[1]        

    app = create_app(c)

    with app.app.app_context():
        app.run(
            host=current_app.config["IP"], 
            port=current_app.config["PORT"], 
            debug=current_app.config["DEBUG"]
            )
