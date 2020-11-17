from datetime import date
import unittest 
import datetime

from bookings.utils import get_restaurant, get_tables, restaurant_is_open, get_a_table, update_booking

from bookings.app import create_app 

from flask import current_app

class BookingsUtilsTests(unittest.TestCase):
    """ Tests utility functions with and without mocks (uses fake data in case of mocks) """

############################ 
#### setup and teardown #### 
############################ 

    # executed prior to each test 
    def setUp(self): 
        app = create_app("TEST") # Test with mocks (default)
        self.app = app.app 
        self.app.config['TESTING'] = True 

    # executed after each test 
    def tearDown(self): 
        pass 

###############
#### tests #### 
############### 
    def test_get_a_table(self):
        """ Try get a table utils """
        now = datetime.datetime.now()

        with self.app.app_context():
            booking = (now + datetime.timedelta(days=1))
            r = get_a_table(3, 1, booking)
            self.assertEqual(r, 6, msg=r) # expected table 6

            r = get_a_table(3, 4, booking)
            self.assertEqual(r, 5, msg=r) # expected table 5

            r = get_a_table(3, 5, booking)
            self.assertEqual(r, -1, msg=r) # expected table no table (no free tables with such capacity)

    def test_get_a_table_failure(self):
        """ Try get a table utils without mocks """
        now = datetime.datetime.now()

        app = create_app("FAILURE_TEST") # Test without mocks (FAILURE_TEST is configuration in config.ini that disable mocks but maintains fake data)
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            booking = (now + datetime.timedelta(days=1))
            r = get_a_table(3, 1, booking)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_a_table(3, 4, booking)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_a_table(3, 5, booking)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

    def test_get_restaurants_mocked(self):
        """ Test get a restaurant profile with mocks """
        with self.app.app_context():
            r = get_restaurant(1)
            self.assertEqual(r["id"], 1, msg=r) # right object

            r = get_restaurant(0)
            self.assertEqual(r, None, msg=r) # not found ( ids in range 1-4) in faked data

            r = get_restaurant(5)
            self.assertEqual(r, None, msg=r) # not found ( ids in range 1-4) in faked data

    def test_get_restaurants_failure(self):
        """ Try get a restaurant's profile utils without mocks """
        app = create_app("FAILURE_TEST") # Test without mocks (FAILURE_TEST is configuration in config.ini that disable mocks but maintains fake data)
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            r = get_restaurant(1)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_restaurant(0)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_restaurant(5)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

    def test_get_tables_mocked(self):
        """ Test get a restaurant's tables with mocks """
        with self.app.app_context():
            r = get_tables(3)
            self.assertEqual(r, [{"id":4, "capacity":5}, {"id":5, "capacity":4}, {"id":6, "capacity":2}], msg=r) # right tables

            r = get_tables(0)
            self.assertEqual(r, None, msg=r) # not found ( ids in range 1-4) in faked data

            r = get_tables(5)
            self.assertEqual(r, None, msg=r) # not found ( ids in range 1-4) in faked data

    def test_get_tables_failure(self):
        """ Try get a restaurant's tables utils without mocks """
        app = create_app("FAILURE_TEST") # Test without mocks (FAILURE_TEST is configuration in config.ini that disable mocks but maintains fake data)
        app = app.app 
        app.config['TESTING'] = True

        with app.app_context():
            r = get_tables(1)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_tables(0)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

            r = get_tables(5)
            self.assertEqual(r, None, msg=r) # expected None in case of connections problems

    def test_restaurant_is_open(self):
        """ Test if a restaurant is open on a datetime with mocks """
        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with self.app.app_context():
            r,_ = restaurant_is_open(1, booking) # This open
            self.assertEqual(r, False)

            for i in [2,3,4]: # These closed
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, True, msg=i)

            booking = now.replace( year=2020, month=11, day=17, hour=23, minute=0, second=0, microsecond=0 )

            for i in [1,2]: # These open
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, False, msg=i)

            for i in [3,4]: # These closed
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, True, msg=i)

            booking = now.replace( year=2020, month=11, day=16, hour=23, minute=0, second=0, microsecond=0 )
            
            for i in [1,2,4]: # These closed
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, False, msg=i)

            r,_ = restaurant_is_open(3, booking) # This open
            self.assertEqual(r, True)


    def test_restaurant_is_open_failure(self):
        """ Try restaurant is open on a datetime utils without mocks """
        app = create_app("FAILURE_TEST") # Test without mocks (FAILURE_TEST is configuration in config.ini that disable mocks but maintains fake data)
        app = app.app 
        app.config['TESTING'] = True

        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with app.app_context():
            for i in [1,2,3,4]:
                r,_ = restaurant_is_open(i, booking)
                self.assertEqual(r, None, msg=i) # expected None in case of connections problems (for all)

    def test_get_table_restaurant_closed(self):
        """ Try to get a free table in a closed restaurant with mocks """
        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with self.app.app_context():
            r = get_a_table(1, 1, booking)
            self.assertEqual(r, -2) # -2 in case that the restaurant is closed

            booking = now.replace( year=2020, month=11, day=17, hour=23, minute=0, second=0, microsecond=0 )

            for i in [1,2]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, -2, msg=i) # -2 in case that the restaurant is closed

            booking = now.replace( year=2020, month=11, day=16, hour=23, minute=0, second=0, microsecond=0 )
            
            for i in [1,2,4]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, -2, msg=i) # -2 in case that the restaurant is closed


    def test_get_table_restaurant_closed_failure(self):
        """ Try get a table utils without mocks """
        app = create_app("FAILURE_TEST") # Test without mocks (FAILURE_TEST is configuration in config.ini that disable mocks but maintains fake data)
        app = app.app 
        app.config['TESTING'] = True

        now = datetime.datetime.now()
        booking = now.replace( year=2020, month=11, day=17, hour=11, minute=30, second=0, microsecond=0)

        with app.app_context():
            for i in [1,2,3,4]:
                r = get_a_table(i, 1, booking)
                self.assertEqual(r, None, msg=i) # expected None in case of connections problems

    def test_update_booking_wrong_id(self):
        """ Try to update a booking with a very big id (not in fake data) """
        with self.app.app_context():
            self.assertEqual(None,update_booking(999, 2, datetime.datetime.now(), 1)) # not found ( ids in range 1-4) in faked data