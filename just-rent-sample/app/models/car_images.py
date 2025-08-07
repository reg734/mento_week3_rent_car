from app import db
from datetime import datetime

class CarImages(db.Model):
    __tablename__ = 'cars_images'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 關聯到 Car 表
    car = db.relationship('Car', backref='images')
    # 關聯到 User 表 - 明確指定 foreign_keys
    user = db.relationship('User', backref='car_images', foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<CarImages(id={self.id}, car_id={self.car_id}, image_url={self.image_url})>"
