import datetime
import logging
import random
import os

from flask import current_app

from bookings.orm import db, Booking

def use_mocks():
    with current_app.app_context():
        return current_app.config["USE_MOCKS"]

def add_booking(user_id, rest_id, number_of_people, booking_datetime, table_id, entrance_datetime=None):
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

def get_a_table(restaurant_id, number_of_people, booking_datetime):

    if use_mocks():
        is_open = restaurant_is_open(restaurant_id,booking_datetime)
        if is_open is None:
            return None
        if not is_open:
            return -1

        x = random.randint(0,2)
        if x == 0:
            return None
        return x
    else:
        return None

def restaurant_is_open(restaurant_id, booking_datetime):
    if use_mocks():
        x = random.randint(0,3)
        if x == 0:
            return None
        elif x == 1:
            return True
        return False
    else:   
        return None


def put_fake_data():
    """
        USERS:
            - 1: NO BOOKINGS 
            - 2: 2 OLD BOOKINGS 
            - 3: 1 NEW AND 1 OLD 
            - 4: 2 NEW 
        
        RESTAURANTS:
            - 1: NO BOOKINGS 
            - 2: 2 OLD BOOKINGS 
            - 3: 2 NEW AND 1 OLD 
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
            - 4: TABLE WITH A OLD AND A NEW BOOKING
                - CAPACITY: 5
                - REST: 3
                - BOOKINGS: [2, 6]
            - 5: TABLE WITH A NEW BOOKING
                - CAPACITY: 4
                - REST: 3
                - BOOKINGS: [5]
    """

    # (user_id, rest_id, number_of_people, booking_datetime, table_id)
    
    # 1: FUTURE BOOKING (USER 3, REST 4, TABLE 3)
    add_booking(3, 4, 2, (datetime.datetime.now() + datetime.timedelta(days=2)), 3) 
    
    # 2: FUTURE BOOKING (USER 4, REST 3, TABLE 4)
    add_booking(4, 3, 1, (datetime.datetime.now() + datetime.timedelta(days=1)), 4)
    
    # 3: OLD BOOKING (USER 2, REST 2, TABLE 2)
    add_booking(2, 2, 3, (datetime.datetime.now()), 2)
    
    # 4: OLD BOOKING (USER 2, REST 2, TABLE 2)
    add_booking(2, 2, 3, (datetime.datetime.now() - datetime.timedelta(days=1)), 2)
    
    # 5: FUTURE BOOKING (USER 4, REST 3, TABLE 5)
    add_booking(4, 3, 1, (datetime.datetime.now() + datetime.timedelta(days=2)), 5)
    
    # 6: OLD BOOKING (USER 3, REST 3, TABLE 4)
    add_booking(3, 3, 1, (datetime.datetime.now() - datetime.timedelta(days=2)), 4)