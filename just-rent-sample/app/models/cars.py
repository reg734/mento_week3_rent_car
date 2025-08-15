
from app import db
from datetime import datetime

class Car(db.Model):
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    body = db.Column(db.String(100), nullable=False, default='Unknown')
    seats = db.Column(db.Integer, nullable=False, default=5)
    doors = db.Column(db.Integer, nullable=False, default=4)
    luggage_capacity = db.Column(db.Integer, nullable=True)
    fuel_type = db.Column(db.String(50), nullable=False, default='汽油')
    engine = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    mileage = db.Column(db.Integer, nullable=False, default=0)
    transmission = db.Column(db.String(50), nullable=True)
    drive_type = db.Column(db.String(20), nullable=True)
    fuel_economy = db.Column(db.Float, nullable=True)
    exterior_color = db.Column(db.String(50), nullable=False, default='Unknown')
    interior_color = db.Column(db.String(50), nullable=False, default='Unknown')
    car_level = db.Column(db.Integer, nullable=False, default=1)
    
    created_at = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow,
                            server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow,
                            server_default=db.func.current_timestamp(),
                            onupdate=datetime.utcnow)

def __repr__(self):
    return f"<Car(name={self.name}, brand={self.brand}, year={self.year}, body={self.body}, seats={self.seats}, doors={self.doors}, luggage_capacity={self.luggage_capacity}, fuel_type={self.fuel_type}, engine={self.engine}, transmission={self.transmission}, drive_type={self.drive_type}, mileage={self.mileage}, fuel_economy={self.fuel_economy}, exterior_color={self.exterior_color}, interior_color={self.interior_color}, car_level={self.car_level})>"