from app import db
from app.api import bp
from flask import jsonify, abort
from sqlalchemy import text

@bp.route('/api/cars', methods=['GET'])
def get_cars():
    sql = text('SELECT id, name, seat, door, body, displacement, car_type, seat_number, door_number, car_length, wheelbase, power_type, brand, model FROM cars')
    result = db.session.execute(sql)

    cars_list = [dict(row._mapping) for row in result]

    return jsonify(cars_list)

@bp.route('/api/cars/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    # 獲取車輛基本資訊
    car_sql = text('SELECT id, name, brand, year, body, seats, doors, luggage_capacity, fuel_type, engine, transmission, drive_type, mileage, fuel_economy, exterior_color, interior_color FROM cars WHERE id = :car_id')
    car_result = db.session.execute(car_sql, {'car_id': car_id}).fetchone()

    if not car_result:
        abort(404, description="Car not found")

    car = dict(car_result._mapping)  # 將結果轉換為字典

    # 獲取車輛圖片
    images_sql = text('SELECT image_url FROM cars_images WHERE car_id = :car_id')
    images_result = db.session.execute(images_sql, {'car_id': car_id}).fetchall()

    # 使用 row._mapping 訪問資料
    car['images'] = [row._mapping['image_url'] for row in images_result]

    return jsonify(car)