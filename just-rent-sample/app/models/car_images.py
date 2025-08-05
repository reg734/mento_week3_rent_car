from app import db

class CarImages(db.Model):
    __tablename__ = 'cars_images'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False) 

    # 關聯到 Car 表
    car = db.relationship('Car', backref='images')

    def __repr__(self):
        return f"<CarImages(id={self.id}, car_id={self.car_id}, image_url={self.image_url})>"
