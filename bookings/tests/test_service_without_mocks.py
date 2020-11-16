import unittest 
import datetime

from bookings.app import create_app 

class BookingsFailureTests(unittest.TestCase): 

    ############################ 
    #### setup and teardown #### 
    ############################ 

    # executed prior to each test 
    def setUp(self): 
        app = create_app("FAILURE_TEST") 
        self.app = app.app 
        self.app.config['TESTING'] = True 

    # executed after each test 
    def tearDown(self): 
        pass 

###############
#### tests #### 
############### 

    def test_post_bookings(self): 
        client = self.app.test_client() 
        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":3, 
            "booking_datetime": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 500, msg=json) 

    def test_put_bookings(self):
        client = self.app.test_client()
        booking = {
            "number_of_people":2
            }
        response = client.put('/bookings/2',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 500, msg=json)

   