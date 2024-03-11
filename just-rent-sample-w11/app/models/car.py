from app import db

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, default='Unknown')
    seat = db.Column(db.Integer, nullable=False, default=0)
    door = db.Column(db.Integer, nullable=False, default=0)
    body = db.Column(db.String(255), nullable=False, default='Unknown')
    displacement = db.Column(db.String(255), nullable=False, default='Unknown')
    car_type = db.Column(db.String(255), nullable=False, default='Unknown')
    seat_number = db.Column(db.String(255), nullable=False, default='Unknown')
    door_number = db.Column(db.String(255), nullable=False, default='Unknown')
    car_length = db.Column(db.String(255), nullable=False, default='Unknown')
    wheelbase = db.Column(db.String(255), nullable=False, default='Unknown')
    power_type = db.Column(db.String(255), nullable=False, default='Unknown')
    brand = db.Column(db.String(255))
    model = db.Column(db.String(255))