from datetime import date
import unittest 
import datetime

from bookings.utils import get_restaurant, get_tables, restaurant_is_open, get_a_table, update_booking

from bookings.app import create_app 

from flask import current_app

class BookingsFailureTests(unittest.TestCase): 

############################ 
#### setup and teardown #### 
############################ 

    # executed prior to each test 
    def setUp(self): 
        app = create_app("TEST") 
        self.app = app.app 
        self.app.config['TESTING'] = True 

    # executed after each test 
    def tearDown(self): 
        pass 

###############
#### tests #### 
############### 
    def test_get_a_table(self):
        now = datetime.datetime.now()

        with self.app.app_context():
            booking = (now + datetime.timedelta(days=1))
            r = get_a_table(3, 1, booking)
            self.assertEqual(r, 6, msg=r)

            r = get_a_table(3, 4, booking)
            self.assertEqual(r, 5, msg=r)

            r = get_a_table(3, 5, booking)
            self.assertEqual(r, -1, msg=r)

    def test_get_a_table_failure(self):
        now = datetime.datetime.now()

        app = create_app("FAILURE_TEST") 
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            booking = (now + datetime.timedelta(days=1))
            r = get_a_table(3, 1, booking)
            self.assertEqual(r, None, msg=r)

            r = get_a_table(3, 4, booking)
            self.assertEqual(r, None, msg=r)

            r = get_a_table(3, 5, booking)
            self.assertEqual(r, None, msg=r)

    def test_get_restaurants_mocked(self):
        with self.app.app_context():
            r = get_restaurant(1)
            self.assertEqual(r["id"], 1, msg=r)

            r = get_restaurant(0)
            self.assertEqual(r, None, msg=r)

            r = get_restaurant(5)
            self.assertEqual(r, None, msg=r)

    def test_get_restaurants_failure(self):

        app = create_app("FAILURE_TEST") 
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            r = get_restaurant(1)
            self.assertEqual(r, None, msg=r)

            r = get_restaurant(0)
            self.assertEqual(r, None, msg=r)

            r = get_restaurant(5)
            self.assertEqual(r, None, msg=r)

    def test_get_tables_mocked(self):
        with self.app.app_context():
            r = get_tables(3)
            self.assertEqual(r, [{"id":4, "capacity":5}, {"id":5, "capacity":4}, {"id":6, "capacity":2}], msg=r)

            r = get_tables(0)
            self.assertEqual(r, None, msg=r)

            r = get_tables(5)
            self.assertEqual(r, None, msg=r)

    def test_get_tables_failure(self):

        app = create_app("FAILURE_TEST") 
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            r = get_tables(1)
            self.assertEqual(r, None, msg=r)

            r = get_tables(0)
            self.assertEqual(r, None, msg=r)

            r = get_tables(5)
            self.assertEqual(r, None, msg=r)

    def test_restaurant_is_open(self):
        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with self.app.app_context():
            r,_ = restaurant_is_open(1, booking)
            self.assertEqual(r, False)

            for i in [2,3,4]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, True, msg=i)

            booking = now.replace( year=2020, month=11, day=17, hour=23, minute=0, second=0, microsecond=0 )

            for i in [1,2]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, False, msg=i)

            for i in [3,4]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, True, msg=i)

            booking = now.replace( year=2020, month=11, day=16, hour=23, minute=0, second=0, microsecond=0 )
            
            for i in [1,2,4]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, False, msg=i)

            r,_ = restaurant_is_open(3, booking)
            self.assertEqual(r, True)


    def test_restaurant_is_open_failure(self):
    
        app = create_app("FAILURE_TEST") 
        app = app.app 
        app.config['TESTING'] = True

        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with app.app_context():
            for i in [1,2,3,4]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, None, msg=i)

    def test_get_table_restaurant_closed(self):
        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with self.app.app_context():
            r = get_a_table(1, 1, booking)
            self.assertEqual(r, -1)

            booking = now.replace( year=2020, month=11, day=17, hour=23, minute=0, second=0, microsecond=0 )

            for i in [1,2]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, -1, msg=i)

            booking = now.replace( year=2020, month=11, day=16, hour=23, minute=0, second=0, microsecond=0 )
            
            for i in [1,2,4]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, -1, msg=i)


    def test_get_table_restaurant_closed_failure(self):
    
        app = create_app("FAILURE_TEST") 
        app = app.app 
        app.config['TESTING'] = True

        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with app.app_context():
            for i in [1,2,3,4]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, None, msg=i)

    def test_update_booking_wrong_id(self):
        with self.app.app_context():
            self.assertEqual(None,update_booking(999, 2, datetime.datetime.now(), 1))