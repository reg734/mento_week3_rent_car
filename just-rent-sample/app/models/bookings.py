from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    pick_up_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    drop_off_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    pick_up_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 關聯到 Car 表
    car = db.relationship('Car', backref='bookings')
    # 關聯到 User 表
    user = db.relationship('User', backref='bookings')