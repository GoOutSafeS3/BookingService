import unittest 
import datetime

from bookings.app import create_app 


class BookingsTests(unittest.TestCase): 
    """ Tests endpoints with mocks """

    ############################ 
    #### setup and teardown #### 
    ############################ 

    # executed prior to each test 
    def setUp(self): 
        app = create_app("TEST") # Test with mocks
        self.app = app.app 
        self.app.config['TESTING'] = True 

    # executed after each test 
    def tearDown(self): 
        pass 

###############
#### tests #### 
############### 

    def test_edit_booking_400_409(self):
        """ Tests the edit service with bad requests """
        client = self.app.test_client()

        booking = {}
        response = client.put('/bookings/1',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # empty json

        booking = {
            "number_of_people":1, 
            "booking_datetime":"worngdatetime"
            }
        response = client.put('/bookings/1',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # wrong datetime format

        booking = {
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            }
        response = client.put('/bookings/1',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to book before now 

        booking = {
            "number_of_people":0, 
            "booking_datetime": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }
        response = client.put('/bookings/1',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to book for zero people

        booking = {
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13,minute=30,second=0,microsecond=0) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.put('/bookings/1',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 409, msg=json) # good request but impossible to do (closed restaurant)

        booking = {
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }
        response = client.put('/bookings/6',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to change a past booking

        booking = {
            "number_of_people":1, 
            }
        response = client.put('/bookings/7',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to change a past booking

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":3, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking) # first i create a new booking
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # good request: created
        self.assertEqual(json["table_id"], 5, msg=json) # right table

        booking = {
            "number_of_people":10, 
            }
        response = client.put('/bookings/'+str(json["id"]),json=booking) # i try to change the booking increasing the capacity but there are no tables with such capacity
        json = response.get_json()
        self.assertEqual(response.status_code, 409, msg=json) # no free tables (now) no free tables with such capacity


    def test_edit_booking(self):
        """ Tests the edit service with good requests """
        client = self.app.test_client()

        now = datetime.datetime.now().replace(hour=13)

        response = client.get('/bookings?rest=3&begin='+now.isoformat()+"Z")
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        self.assertEqual(len(json), 2, msg=json) # just for safety

        booking = {
            "number_of_people":2
            }
        response = client.put('/bookings/2',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json) # good request
        response = client.get('/bookings?rest=3&begin='+now.isoformat()+"Z") # just to check
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        self.assertEqual(len(json), 2, msg=json)
        self.assertEqual(json[0]["id"], 2, msg=json) # same id
        self.assertEqual(json[0]["number_of_people"], 2, msg=json) # right number

        booking = {
            "booking_datetime": (now + datetime.timedelta(days=1)).isoformat()+"Z"
            }
        response = client.put('/bookings/2',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json) # good request
        response = client.get('/bookings?rest=3&begin='+now.isoformat()+"Z") # just to check
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 2, msg=json)
        self.assertEqual(json[0]["id"], 2, msg=json) # same id
        self.assertEqual(json[0]["booking_datetime"], (now + datetime.timedelta(days=1)).isoformat()+"Z", msg=json) # right datetime

        booking = {
            "number_of_people":3,
            "booking_datetime": (now + datetime.timedelta(days=2)).isoformat()+"Z"
            }
        response = client.put('/bookings/2',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json) # good request
        response = client.get('/bookings?rest=3&begin='+now.isoformat()+"Z") # just to check
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        self.assertEqual(len(json), 2, msg=json)
        self.assertEqual(json[0]["id"], 2, msg=json) # same id
        self.assertEqual(json[0]["number_of_people"], 3, msg=json) # right number
        self.assertEqual(json[0]["booking_datetime"], (now + datetime.timedelta(days=2)).isoformat()+"Z", msg=json) # right datetime

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking) # first i create a new booking
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # good request: created
        self.assertEqual(json["table_id"], 6, msg=json) # right table

        response = client.post('/bookings',json=booking) # and another booking
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # good request: created
        self.assertEqual(json["table_id"], 5, msg=json) # right table

        response = client.post('/bookings',json=booking) # and another booking
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # good request: created
        self.assertEqual(json["table_id"], 4, msg=json) # right table


        """ Now there is no more space in restaurant 3 """

        booking = {
            "number_of_people":2, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13,minute=30) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.put('/bookings/9',json=booking) # but i can change my booking if the same table i booked is still good 
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json) # the requeste is accepted because the table i had is still good
        self.assertEqual(json["table_id"], 6, msg=json) # still the same table
    
    def test_new_booking_400_409(self):
        """ Tests the new bookings service with bad requests """
        client = self.app.test_client()

        booking = {}
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # empty json

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":1, 
            "booking_datetime":"worngdatetime"
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # wrong datetime format

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to book before now 

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":0, 
            "booking_datetime": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # try to book for zero people

        booking = {
            "user_id":1,
            "restaurant_id":2,
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now().replace(hour=18) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 409, msg=json) # try to book in a closed restaurant

    def test_new_booking(self):
        """ Tests the new bookings service with good requests """
        client = self.app.test_client()

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":3, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # good request: created
        self.assertEqual(json["table_id"], 5, msg=json) # right table

        response = client.post('/bookings',json=booking) # same booking again
        json = response.get_json()
        self.assertEqual(response.status_code, 409, msg=json) # no free tables (now) 'cause too much people (no free tables with such capacity)

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":2, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 201, msg=json) # another good request
        self.assertEqual(json["table_id"], 6, msg=json) # there is a table for 2 people

        booking = {
            "user_id":1,
            "restaurant_id":3,
            "number_of_people":1, 
            "booking_datetime": (datetime.datetime.now().replace(hour=13) + datetime.timedelta(days=1)).isoformat()
            }
        response = client.post('/bookings',json=booking)
        json = response.get_json()
        self.assertEqual(response.status_code, 409, msg=json) # no free tables (now)

    def test_404(self): 
        """ Tests that all the endpoints that manage ids responds with 404 in case of not found error """
        client = self.app.test_client() 

        """ the endpoints and methods to test """
        endpoints = { 
             "/bookings/":["get","put","delete"]  
         } 
        for k,v in endpoints.items(): 
            for m in v: 
                response = None 
                if m == "get": 
                    response = client.get(k+'999') 
                elif m == "put": 
                    response = client.put(k+'999',json={}) 
                elif m == "delete": 
                    response = client.delete(k+'999') 
                self.assertEqual(response.status_code, 404, msg="ENDPOINT: "+k+"\nMETHOD: "+m+"\n"+response.get_data(as_text=True)) # not found

    def test_get_bookings(self): 
        """ Tests get the list of all bookings """
        client = self.app.test_client() 
        response = client.get('/bookings') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # OK
        self.assertEqual(len(json), 8, msg=json) # right length

    def test_bookings_filter_by_id(self): 
        """ Tests get the list of all bookings that match the filters (only filters that work with ids)"""
        client = self.app.test_client() 

        response = client.get('/bookings?user=user') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) # wrong request (user must be an integer)

        response = client.get('/bookings?user=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json)  
        self.assertEqual(len(json), 0, msg=json) # right request but zero bookings

        response = client.get('/bookings?user=3') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 3, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [1,6, 8], msg=json)

        response = client.get('/bookings?rest=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json) # right request but zero bookings

        response = client.get('/bookings?rest=3') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 5, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [2,5,6,7,8], msg=json)

        response = client.get('/bookings?table=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json)  # right request but zero bookings

        response = client.get('/bookings?table=4') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 3, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [2,6,8], msg=json)

        response = client.get('/bookings?rest=4&user=2') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json)  # right request but zero bookings

        response = client.get('/bookings?user=2&table2') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 2, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [3,4], msg=json)  # a "safety" check

    def test_bookings_filter_by_date(self): 
        """ Tests get the list of all bookings that match the filters (only filters that work with datetimes)"""
        client = self.app.test_client() 

        now = datetime.datetime.now().isoformat()

        response = client.get('/bookings?begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 3, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [1,2,5], msg=json) # a "safety" check

        response = client.get('/bookings?end='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 5, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [3,4,6,7,8], msg=json) # a "safety" check

        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
        response = client.get('/bookings?begin='+now+'&end='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 1, msg=json) 
        self.assertEqual(json[0]["id"], 2, msg=json) # right request

    def test_bookings_filter_by_entrance_date(self): 
        """ Tests get the list of all bookings that match the filters (only filters that work with entrance datetimes)"""
        client = self.app.test_client() 

        now = datetime.datetime.now().isoformat()

        """ There are no bookings with entrance in this moment """

        response = client.get('/bookings?begin_entrance='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 0, msg=json) # right request but no entrance zero

        response = client.get('/bookings?end_entrance='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 0, msg=json) # right request but no entrance so zero

        response = client.put('/bookings/2?entrance=true',json={})  # set the entrance 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # good request: marked
        self.assertEqual(json["id"], 2, msg=json) # a "safety" check
        self.assertIsNotNone(json["entrance_datetime"], msg=json) # another "safety" check

        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
        response = client.get('/bookings?begin_entrance='+now+'&end_entrance='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 1, msg=json) 
        self.assertEqual(json[0]["id"], 2, msg=json) # right request

        response = client.put('/bookings/1?entrance=true',json={})  # set another entrance 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # good request: marked
        self.assertEqual(json["id"], 1, msg=json) # a "safety" check
        self.assertIsNotNone(json["entrance_datetime"], msg=json) # another "safety" check

        response = client.get('/bookings?begin_entrance='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 2, msg=json) # right request
        for e in json:
            self.assertIn(e["id"], [1,2], msg=json) # a "safety" check


        response = client.get('/bookings?end_entrance='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 2, msg=json) # right 
        for e in json:
            self.assertIn(e["id"], [1,2], msg=json) # a "safety" check


    def test_bookings_filter_wrong_date(self): 
        """ Tests get the list of all bookings that match the filters (only filters that work with datetimes)
        with wrong datetime format
        """
        client = self.app.test_client() 

        now = "now"

        response = client.get('/bookings?begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) # bad format

        response = client.get('/bookings?end='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True))  # bad format

        tomorrow = "tomorrow"
        response = client.get('/bookings?begin='+now+'&end='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) # bad formats

    def test_bookings_filter_wrong_entrance_date(self): 
        """ Tests get the list of all bookings that match the filters (only filters that work with entrance datetimes)
        with wrong datetime format
        """
        client = self.app.test_client() 

        now = "now"

        response = client.get('/bookings?begin_entrance='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) # bad format

        response = client.get('/bookings?end_entrance='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True))  # bad format

        tomorrow = "tomorrow"
        response = client.get('/bookings?begin_entrance='+now+'&end='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) # bad formats


    def test_bookings_filter_id_and_date(self):
        """ Tests get the list of all bookings that match the filters (both ids and datetimes)"""
        client = self.app.test_client() 

        now = datetime.datetime.now().isoformat()
        response = client.get('/bookings?user=4&begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 2, msg=json) # good request
        for e in json:
            self.assertIn(e["id"], [2,5], msg=json) # a "safety" check

        now = "now"
        response = client.get('/bookings?user=4&begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) # bad datetime format

    def test_get_booking(self): 
        """ Tests the get a specific booking (by id) service """ 
        client = self.app.test_client() 
        response = client.get('/bookings/1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # good request

    def test_delete_old_booking(self): 
        """ Try to delete an old booking """ 
        client = self.app.test_client() 
        response = client.delete('/bookings/6') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 403, msg=json) # forbidden

    def test_delete_future_booking(self):
        """ Try to delete a future booking""" 
        client = self.app.test_client() 
        response = client.delete('/bookings/1') 
        self.assertEqual(response.status_code, 204) # good request: deleted
 
    def test_empty_put(self): 
        """ Try to edit a booking with an empty json """
        client = self.app.test_client() 
        response = client.put('/bookings/1',json={}) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) # bad request

    def test_set_entrance(self): 
        """ Try to set the ntrance of a booking """
        client = self.app.test_client() 

        response = client.put('/bookings/1?entrance=true',json={}) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # good request: marked
        self.assertEqual(json["id"], 1, msg=json) # a "safety" check
        self.assertIsNotNone(json["entrance_datetime"], msg=json) # another "safety" check

        response = client.put('/bookings/1?entrance=true',json={}) # re-try
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) # forbidden (already marked)


    def test_set_entrance_then_try_to_change(self): 
        """ Set the entrance then try to change (forbidden) """
        client = self.app.test_client() 

        response = client.put('/bookings/2?entrance=true',json={}) # se the entrance
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) # OK
        self.assertEqual(json["id"], 2, msg=json) # a "safety" check
        self.assertIsNotNone(json["entrance_datetime"], msg=json) # another "safety" check

        
        booking = {
            "number_of_people":2
            }
        response = client.put('/bookings/2',json=booking) # try to change
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json) # forbidden