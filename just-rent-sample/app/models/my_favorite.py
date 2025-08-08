from app import db

class MyFavorites(db.Model):
    __tablename__ = 'my_favorites'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    car = db.relationship('Car', backref='favorite_entries')
    user = db.relationship('User', backref='favorite_entries')

    def __repr__(self):
        return f"<MyFavorites(id={self.id}, car_id={self.car_id}, user_id={self.user_id})>"
