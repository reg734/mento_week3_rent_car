from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'),
nullable=False, unique=True)
    payment_status = db.Column(db.String(20), nullable=False,
default='pending')
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(255), nullable=True)
    transaction_id = db.Column(db.String(255), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, nullable=False,
default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)

    # 關聯到 Booking 表 (一對一關係)
    booking = db.relationship('Booking', backref=db.backref('order',
uselist=False))

    def __repr__(self):
        return f"<Order(id={self.id}, booking_id={self.booking_id}, status={self.payment_status}, amount={self.amount})>"