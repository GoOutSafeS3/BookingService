import unittest 
from booking.app import create_app 

class BookingsTests(unittest.TestCase): 

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

    def test_404(self): 
        client = self.app.test_client() 
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
                self.assertEqual(response.status_code, 404, msg="ENDPOINT: "+k+"\nMETHOD: "+m+"\n"+response.get_data(as_text=True)) 

 

    def test_get_bookings(self): 
        client = self.app.test_client() 
        response = client.get('/bookings') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 6, msg=json) 

    def test_bookings_filters(self): 
        client = self.app.test_client() 
        response = client.get('/bookings?id=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 1, msg=json) 
        self.assertEqual(json["id"], 1, msg=json) 
        self.assertEqual(json[0]["id"], 1, msg=json) 

    def test_get_booking(self): 

        client = self.app.test_client() 
        response = client.get('/bookings/1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 

    def test_delete_old_booking(self): 
        client = self.app.test_client() 
        response = client.delete('/bookings/6') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 403, msg=json) 

    def test_delete_future_booking(self): 
        client = self.app.test_client() 
        response = client.delete('/bookings/1') 
        self.assertEqual(response.status_code, 204) 
 
    def test_empty_put(self): 
        client = self.app.test_client() 
        response = client.put('/bookings/1',json={}) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) 

    def test_set_entrance(self): 

        client = self.app.test_client() 

        response = client.put('/bookings/1?entrance=true',json={}) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(json["id"], 1, msg=json) 
        self.assertIsNotNone(json["entrance_datetime"], msg=json) 

        response = client.put('/bookings/1?entrance=true',json={}) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) 