
from app import db
from datetime import datetime, timezone, timedelta

class PopularCar(db.Model):
    __tablename__ = 'popular_cars'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)
    # 使用台灣時間而不是 UTC 時間
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 建立與 Car model 的關聯（假設你有 Car model）
    car = db.relationship('Car', backref='popular_entries')
    
    def __repr__(self):
        return f'<PopularCar {self.id}: Car {self.car_id}, Order {self.sort_order}>'
