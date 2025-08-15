from app import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 因為 Booking 有兩個外鍵指向 Location（pick_up_location_id 和 drop_off_location_id）
    # 需要分別定義兩個 relationship
    pick_up_bookings = db.relationship('Booking', foreign_keys='Booking.pick_up_location_id', backref='pick_up_location')
    drop_off_bookings = db.relationship('Booking', foreign_keys='Booking.drop_off_location_id', backref='drop_off_location')
