import sys
import os

# 加入專案根目錄，讓 Python 找到 app 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Car

app = create_app()

with app.app_context():
    car = Car(
        name='2016 Suzuki Swift 1.2 GLX',
        brand='Suzuki',
        year=2016,
        body='掀背車',
        door=5,
        door_number='5門',
        seat=5,
        seat_number='5人座',
        car_length='3850mm',
        wheelbase='2430mm',
        exterior_color='Unknown',
        interior_color='Unknown',
        engine='1242cc',
        power_type='汽油',
        fuel_economy=None,
        transmission='Unknown',
        drive='Unknown',
        luggage=None,
        mileage=None,
        vehicle_type='轎車'
    )

    db.session.add(car)
    db.session.commit()

    print("✅ 成功新增一筆 Suzuki Swift 資料")