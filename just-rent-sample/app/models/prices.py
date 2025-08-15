from app import db
from datetime import datetime
from sqlalchemy.orm import foreign

class Price(db.Model):
    __tablename__ = 'prices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='normal')
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # relationship: 取得所有該等級的車
    cars = db.relationship('Car', 
                          primaryjoin='Price.level==foreign(Car.car_level)', 
                          viewonly=True)

    def __repr__(self):
        return f"<Price(level={self.level}, type={self.type}, price={self.price})>"