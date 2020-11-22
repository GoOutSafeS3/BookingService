import datetime
import requests

from flask import current_app

from bookings.orm import db, Booking

""" The list of restaurants used when the mocks are required 
    
    They are identified starting from 1.
"""
restaurants = [
    {
        "url": "/restaurants/1", # NO OPENING TIMES
        "id": 1,
        "name": "Rest 1",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": None,
        "first_closing_hour": None,
        "second_opening_hour": None,
        "second_closing_hour": None,
        "occupation_time": 0,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1,2,3,4,5,6,7]
    },
    {
        "url": "/restaurants/2", # ONLY AT LUNCH (CLOSED ON MONDAYS)
        "id": 2,
        "name": "Rest 2",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 10,
        "first_closing_hour": 14,
        "second_opening_hour": None,
        "second_closing_hour": None,
        "occupation_time": 1,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1]
    },
    {
        "url": "/restaurants/3", # ALWAYS OPEN (NEVER CLOSED)
        "id": 3,
        "name": "Rest 3",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 0,
        "first_closing_hour": 23,
        "second_opening_hour": None,
        "second_closing_hour": None,
        "occupation_time": 2,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": []
    },
    {
        "url": "/restaurants/4", # TWO OPENINGS (CLOSED ON SUNDAY AND MONDAYS)
        "id": 4,
        "name": "Rest 4",
        "rating_val": 3.4,
        "rating_num": 123,
        "lat": 42.42,
        "lon": 42.42,
        "phone": "050123456",
        "first_opening_hour": 10,
        "first_closing_hour": 12,
        "second_opening_hour": 20,
        "second_closing_hour": 23,
        "occupation_time": 2,
        "cuisine_type": "cuisine_type",
        "menu": "menu",
        "closed_days": [1, 7]
    }
]

""" The list of tables for each restaurant used when the mocks are required 
    
    They are identified starting from 1.
"""
tables = [
    [{"id":1, "capacity":4}],
    [{"id":2, "capacity":3}],
    [{"id":4, "capacity":5}, {"id":5, "capacity":4}, {"id":6, "capacity":2}],
    [{"id":3, "capacity":2}]
]

def get_from(url):
    """ Makes a get request with a timeout.

    Returns the json object if the code is 200, otherwise None

    The timeout is set in config.ini or the default one is used (0.001)
    """
    try:
        with current_app.app_context():
            r = requests.get(url, timeout=current_app.config["TIMEOUT"])
            if r.status_code == 200:
                return r.json()
            return None
    except:
        return None

def get_restaurant(id):
    """ Get the restaurant json or None 
    
    Use the default ones if mocks are requested
    """
    with current_app.app_context():
        if current_app.config["USE_MOCKS"]:
            id -= 1 # restaurant IDs starting by 1
            if 0 <= id < len(restaurants):
                return restaurants[id]
            else:
                return None
        else:
            return get_from(current_app.config["REST_SERVICE_URL"]+"/restaurants/"+str(id))

def get_tables(id):
    """ Get the list fo the restaurant's tables or None 
    
    Use the default ones if mocks are requested
    """
    with current_app.app_context():
        if current_app.config["USE_MOCKS"]:
            id -= 1 # restaurant IDs starting by 1
            if 0 <= id < len(restaurants):
                return tables[id]
            else:
                return None
        else:
            return get_from(current_app.config["REST_SERVICE_URL"]+"/restaurants/"+str(id)+"/tables")

def add_booking(user_id, rest_id, number_of_people, booking_datetime, table_id, entrance_datetime=None):
    """ Add a new reservation 
    
    Return the booking id, otherwise
    Return None if a db error occured
    """
    try:
        booking = Booking()
        booking.restaurant_id = rest_id
        booking.user_id = user_id
        booking.booking_datetime = booking_datetime
        booking.entrance_datetime = entrance_datetime
        booking.number_of_people = number_of_people
        booking.table_id = table_id
        booking.datetime = datetime.datetime.now()
        db.session.add(booking)
        db.session.commit()
        return booking.id
    except:
        db.session.rollback()
        return None

def update_booking(booking_id, number_of_people, booking_datetime, table_id, entrance_datetime=None):
    """ Edit a reservation specified by the id 
    
    Return the booking id, otherwise
    Return None if a db error occured
    """
    try:
        booking = db.session.query(Booking).filter_by(id = booking_id).first()
        if booking is None:
            return None
        booking.booking_datetime = booking_datetime
        booking.entrance_datetime = entrance_datetime
        booking.number_of_people = number_of_people
        booking.table_id = table_id
        db.session.add(booking)
        db.session.commit()
        return booking.id
    except:
        db.session.rollback()
        return None

def get_a_table(restaurant_id, number_of_people, booking_datetime, excluded=-1):
    """ Return a free table if it is available, otherwise
        - Return -1 if there are no free tables
        - Return -2 if the restaurant is closed

    Return None if it is impossible to connect with the restaurant microservice.

    Parameters:
        - restaurant_id: the id of the restaurant
        - number_of_people: the number of people for the booking
        - booking_datetime: the datetime of the booking
        - excluded: a booking that you want to exclude when searching for free tables 
                    (-1 by default (i.e. no exclusions: the ids are positive)). 
                    It is used only during the edit phase of a booking to prevent the booking you want to modify 
                    from being considered. 
                    For example, if not used, the request to move the booking by half an hour or 
                    add a seat (if the capacity of the table allows it) could not be accepted 
                    as the same booking would be seen as non-modifiable and 
                    another table would be searched, when maybe, what you already have is fine.

    """

    is_open, rest = restaurant_is_open(restaurant_id, booking_datetime) # check is the restaurant is open on that date
    if is_open is None: # connection error with the restaurant microservice
        return None
    if not is_open: 
        return -2

    tables = get_tables(restaurant_id) # return the list of tables of the restaurant

    if tables is None: # connection error with the restaurant microservice
        return None
    if tables == []:
        return -1

    delta = int(rest["occupation_time"])
    starting_period = booking_datetime - datetime.timedelta(hours=delta)
    ending_period = booking_datetime + datetime.timedelta(hours=delta)

    # the list of the tables occupied or booked in the same period as the booking
    occupied = db.session.query(Booking.table_id).select_from(Booking)\
        .filter(Booking.restaurant_id == restaurant_id)\
        .filter(starting_period < Booking.booking_datetime)\
        .filter(Booking.booking_datetime < ending_period )\
        .filter(Booking.id != excluded)\
        .all()
        
    free_tables = [t for t in tables if ( ((t["id"],) not in occupied) and (t["capacity"] >= number_of_people) )] # returns the free table usable by this number of people
    free_tables.sort(key=lambda x:x["capacity"]) # order the tables from the smaller

    if free_tables == []: # no free tables
        return -1
    return free_tables[0]["id"] # return the smaller table that can be used

def restaurant_is_open(restaurant_id, booking_datetime):
    """ Check if a restaurant is open in a given datetime

    Return true if the restaurant is open (with the json of the restaurant)
    Return false if the restaurant is closed (with the json of the restaurant)
    eturn None if it is impossible to connect with the restaurant microservice.
    """
    rest = get_restaurant(restaurant_id)
    if rest is None: # error with the microservice
        return (None,None)
    else:
        if (booking_datetime.weekday()+1) in rest["closed_days"]:
            return (False,rest)
        
        now = datetime.datetime.now()

        booking = now.replace( hour=booking_datetime.hour, minute=booking_datetime.minute, second=0, microsecond=0 )

        if rest["first_opening_hour"] is not None and rest["first_closing_hour"] is not None:
            opening = now.replace( hour=int(rest["first_opening_hour"]), minute=0, second=0, microsecond=0 )
            closing = now.replace( hour=int(rest["first_closing_hour"]), minute=0, second=0, microsecond=0 )

            if opening <= booking <= closing:
                return (True,rest)

        if rest["second_opening_hour"] is not None and rest["second_closing_hour"] is not None:
            opening = now.replace( hour=int(rest["second_opening_hour"]), minute=0, second=0, microsecond=0 )
            closing = now.replace( hour=int(rest["second_closing_hour"]), minute=0, second=0, microsecond=0 )

            if opening <= booking <= closing:
                return (True,rest)

        return (False,rest)


def put_fake_data():
    """
    Enter fake data (useful for testing purposes).

    The properties of the "fake world" are described below
    """

    """
        BOOKINGS:
            - 1: FUTURE BOOKING 
                - USER 3 
                - REST 4 
                - TABLE 3
            - 2: FUTURE BOOKING 
                - USER 4
                - REST 3
                - TABLE 4
            - 3: OLD BOOKING 
                - USER 2
                - REST 2
                - TABLE 2
            - 4: OLD BOOKING 
                - USER 2
                - REST 2
                - TABLE 2
            - 5: FUTURE BOOKING 
                - USER 4
                - REST 3
                - TABLE 5
            - 6: OLD BOOKING 
                - USER 3
                - REST 3
                - TABLE 4
        USERS:
            - 1: NO BOOKINGS 
            - 2: 3 OLD BOOKINGS 
            - 3: 1 NEW AND 2 OLD 
            - 4: 2 NEW 
        
        RESTAURANTS:
            - 1: NO BOOKINGS 
            - 2: 2 OLD BOOKINGS 
            - 3: 2 NEW AND 3 OLD 
            - 4: 1 NEW

        TABLES:
            - 1: NO BOOKINGS 
                - CAPACITY: 4
                - REST: 1
                - BOOKINGS: []
            - 2: 2 OLD BOOKINGS 
                - CAPACITY: 3
                - REST: 2
                - BOOKINGS: [3, 4]
            - 3: TABLE WITH A NEW BOOKING 
                - CAPACITY: 2
                - REST: 4
                - BOOKINGS: [1]
            - 4: TABLE WITH TWO OLD AND A NEW BOOKING
                - CAPACITY: 5
                - REST: 3
                - BOOKINGS: [2, 6, 8]
            - 5: TABLE WITH A NEW BOOKING AND AN OLD
                - CAPACITY: 4
                - REST: 3
                - BOOKINGS: [5, 7]
            - 6: NO BOOKINGS
                - CAPACITY: 2
                - REST: 3
                - BOOKINGS: []
    """

    # add_booking(user_id, rest_id, number_of_people, booking_datetime, table_id)
    
    # 1: FUTURE BOOKING (USER 3, REST 4, TABLE 3)
    add_booking(3, 4, 2, (datetime.datetime.now().replace(hour=10) + datetime.timedelta(days=2)), 3) 
    
    # 2: FUTURE BOOKING (USER 4, REST 3, TABLE 4)
    add_booking(4, 3, 1, (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)), 4)
    
    # 3: OLD BOOKING (USER 2, REST 2, TABLE 2)
    add_booking(2, 2, 3, (datetime.datetime.now().replace(hour=13) - datetime.timedelta(days=3)), 2)
    
    # 4: OLD BOOKING (USER 2, REST 2, TABLE 2)
    add_booking(2, 2, 3, (datetime.datetime.now().replace(hour=13) - datetime.timedelta(days=1)), 2)
    
    # 5: FUTURE BOOKING (USER 4, REST 3, TABLE 5)
    add_booking(4, 3, 1, (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=2)), 5)
    
    # 6: OLD BOOKING (USER 3, REST 3, TABLE 4)
    add_booking(3, 3, 1, (datetime.datetime.now().replace(hour=13) - datetime.timedelta(days=2)), 4)

    # 7: OLD BOOKING (USER 2, REST 3, TABLE 5)
    add_booking(4, 3, 2, (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=10)), 5)
    
    # 8: OLD BOOKING (USER 3, REST 3, TABLE 4)
    add_booking(3, 3, 1, (datetime.datetime.now().replace(hour=13) - datetime.timedelta(days=10)), 4)
