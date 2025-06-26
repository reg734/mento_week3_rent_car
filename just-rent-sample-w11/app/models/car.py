from app import db

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)

    # 基本資訊
    name = db.Column(db.String(255), nullable=False, default='Unknown')
    brand = db.Column(db.String(255))
    year = db.Column(db.Integer)  # 年份

    # 結構與外觀
    body = db.Column(db.String(255), nullable=False, default='Unknown')  # 車身型式
    door = db.Column(db.Integer, nullable=False, default=0)  # 數字型車門數
    door_number = db.Column(db.String(255), nullable=False, default='Unknown')  # 如"2門"
    seat = db.Column(db.Integer, nullable=False, default=0)
    seat_number = db.Column(db.String(255), nullable=False, default='Unknown')
    car_length = db.Column(db.String(255), nullable=False, default='Unknown')
    wheelbase = db.Column(db.String(255), nullable=False, default='Unknown')
    exterior_color = db.Column(db.String(255), default='Unknown')
    interior_color = db.Column(db.String(255), default='Unknown')

    # 引擎與燃料
    engine = db.Column(db.String(255), default='Unknown')  # 新增：如 3000
    power_type = db.Column(db.String(255), nullable=False, default='Unknown')  # 如：汽油、Hybird
    fuel_economy = db.Column(db.Float, default=None)  # 油耗 (km/L 或 MPG)

    # 動力與操控
    transmission = db.Column(db.String(255), default='Unknown')  # 自排/手排
    drive = db.Column(db.String(255), default='Unknown')  # 驅動方式，如 4WD

    # 其他
    luggage = db.Column(db.Integer, default=None)  # 行李空間 (公升)
    mileage = db.Column(db.Float, default=None)  # 里程數（單位需自訂：公里或千公里）
    vehicle_type = db.Column(db.String(255), nullable=False, default='Unknown')  # 車輛類型



