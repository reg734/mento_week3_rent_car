
from app import db
from datetime import datetime

class PopularCar(db.Model):
    __tablename__ = 'popular_cars'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 建立與 Car model 的關聯（假設你有 Car model）
    car = db.relationship('Car', backref='popular_entries')
    
    def __repr__(self):
        return f'<PopularCar {self.id}: Car {self.car_id}, Order {self.sort_order}>'
