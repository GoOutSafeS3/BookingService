from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Booking(db.Model):
    """ Stores the bookings """
    
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    restaurant_id = db.Column(db.Integer)
    number_of_people = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)
    booking_datetime = db.Column(db.DateTime) # the time of  booking
    entrance_datetime = db.Column(db.DateTime, default = None) # the time of entry
    table_id = db.Column(db.Integer)

    def dump(self):
        """ Return a db record as a dict """
        d = dict([(k,v) for k,v in self.__dict__.items() if k[0] != '_'])
        d["url"] = "/bookings/"+str(d["id"])
        return d