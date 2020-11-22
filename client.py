from datetime import datetime

import datetime
import requests

BOOKINGS_SERVICE = "http://localhost:8080/"
TIMEOUT = 2

def _get(url):
    """ Makes a get request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def _post(url,json):
    """ Makes a post request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.post(url, json=json, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def _put(url,json):
    """ Makes a put request with a timeout.

    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.put(url, json=json, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code  
    except:
        return None,None

def _delete(url):
    """ Makes a delete request with a timeout.

    Returns the json object if with the status code (or None, None in case of connection error).
    """
    try:
        r = requests.delete(url, timeout=TIMEOUT)
        try:
            return r.json() ,r.status_code
        except:
            return None, r.status_code   
    except:
        return None,None


def get_bookings(user=None, rest=None, table=None, begin=None, end=None, begin_entrance=None, end_entrance=None):
    url = BOOKINGS_SERVICE+"bookings?"

    if user is not None:
        url += "user="+str(user)+"&"

    if rest is not None:
        url += "rest="+str(rest)+"&"

    if table is not None:
        url += "table="+str(table)+"&"

    if begin is not None:
        url += "begin="+str(begin)+"&"

    if end is not None:
        url += "end="+str(end)+"&"

    if begin_entrance is not None:
        url += "begin_entrance="+str(begin_entrance)+"&"

    if end_entrance is not None:
        url += "end_entrance="+str(end_entrance)+"&"

    return _get(url)

def get_a_booking(id):
    return _get(BOOKINGS_SERVICE+"bookings/"+str(id))

def new_booking(user_id, rest_id, number_of_people, booking_datetime):
    booking = {
        "user_id":user_id,
        "restaurant_id":rest_id,
        "number_of_people":number_of_people,
        "booking_datetime":booking_datetime,
    }

    return _post(BOOKINGS_SERVICE+"bookings",booking)

def edit_booking(booking_id, number_of_people=None, booking_datetime=None, entrance=False):
    booking = {
    }

    if number_of_people is not None:
        booking["number_of_people"] = number_of_people

    if booking_datetime is not None:
        booking["booking_datetime"] = booking_datetime

    url = BOOKINGS_SERVICE+"bookings/"+str(booking_id)

    if entrance:
        url += "?entrance=true"

    return _put(url,booking)

def delete_booking(id):
    return _delete(BOOKINGS_SERVICE+"bookings/"+str(id))

if __name__ == "__main__":
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(edit_booking(7,2),"\n")
    print(edit_booking(7,10),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(7,2,(datetime.datetime.now()+datetime.timedelta(days=2,minutes=30)).isoformat()),"\n")
    print(get_bookings(rest=3),"\n")
    print(get_a_booking(1),"\n")
    print(get_a_booking(100),"\n")
    print(new_booking(1,3,1,(datetime.datetime.now()+datetime.timedelta(days=2)).isoformat()),"\n")
    print(edit_booking(1,1),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(7,1),"\n")
    print(edit_booking(1),"\n")
    print(delete_booking(5),"\n")
    print(delete_booking(6),"\n")
    print(get_bookings(),"\n")
    print(get_bookings(begin_entrance=datetime.datetime.now()-datetime.timedelta(days=1), end_entrance=datetime.datetime.now()+datetime.timedelta(days=2)),"\n")
    print(edit_booking(1,entrance=True),"\n")
    print(get_bookings(begin_entrance=datetime.datetime.now()-datetime.timedelta(days=1), end_entrance=datetime.datetime.now()+datetime.timedelta(days=2)),"\n")