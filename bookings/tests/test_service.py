import unittest 
import datetime

from bookings.app import create_app 

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

    def test_bookings_filter_by_id(self): 
        client = self.app.test_client() 

        response = client.get('/bookings?user=user') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg=json) 

        response = client.get('/bookings?user=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json) 

        response = client.get('/bookings?user=3') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 2, msg=json) 
        for e in json:
            self.assertIn(e["id"], [1,6], msg=json)

        response = client.get('/bookings?rest=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json) 

        response = client.get('/bookings?rest=3') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 3, msg=json)
        for e in json:
            self.assertIn(e["id"], [2,5,6], msg=json)

        response = client.get('/bookings?table=1') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json) 

        response = client.get('/bookings?table=4') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 2, msg=json)
        for e in json:
            self.assertIn(e["id"], [2,6], msg=json)

        response = client.get('/bookings?rest=4&user=2') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 0, msg=json) 

        response = client.get('/bookings?user=2&table2') 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg=json) 
        self.assertEqual(len(json), 2, msg=json)  
        for e in json:
            self.assertIn(e["id"], [3,4], msg=json) 

    def test_bookings_filter_by_date(self): 
        client = self.app.test_client() 

        now = datetime.datetime.now().isoformat()

        response = client.get('/bookings?begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 3, msg=json) 
        for e in json:
            self.assertIn(e["id"], [1,2,5], msg=json) 

        response = client.get('/bookings?end='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 3, msg=json) 
        for e in json:
            self.assertIn(e["id"], [3,4,6], msg=json)  

        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1,hours=1)).isoformat()
        response = client.get('/bookings?begin='+now+'&end='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 1, msg=json) 
        self.assertEqual(json[0]["id"], 2, msg=json)


    def test_bookings_filter_wrong_date(self): 
        client = self.app.test_client() 

        now = "now"

        response = client.get('/bookings?begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 

        response = client.get('/bookings?end='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True))  

        tomorrow = "tomorrow"
        response = client.get('/bookings?begin='+now+'&end='+tomorrow) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetimes: "+now+", "+tomorrow+"\n"+response.get_data(as_text=True)) 

    def test_bookings_filter_id_and_date(self):
        client = self.app.test_client() 

        now = datetime.datetime.now().isoformat()
        response = client.get('/bookings?user=4&begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 200, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 
        self.assertEqual(len(json), 2, msg=json) 
        for e in json:
            self.assertIn(e["id"], [2,5], msg=json) 

        now = "now"
        response = client.get('/bookings?user=4&begin='+now) 
        json = response.get_json() 
        self.assertEqual(response.status_code, 400, msg="Datetime: "+now+"\n"+response.get_data(as_text=True)) 

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