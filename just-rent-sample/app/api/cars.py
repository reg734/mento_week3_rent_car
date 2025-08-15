from app import db
from app.api import bp
from flask import jsonify, abort
from sqlalchemy import text

@bp.route('/api/cars', methods=['GET'])
def get_cars():
    # 先查所有價格，建立 level-price 對照表
    prices_sql = text('SELECT level, price FROM prices WHERE type = "normal"')
    prices_result = db.session.execute(prices_sql).fetchall()
    price_map = {row.level: row.price for row in prices_result}
    sql = text('SELECT * FROM cars')
    result = db.session.execute(sql)

    cars_list = []
    for row in result:
        car = dict(row._mapping)
        # 只取第一張圖片
        image_sql = text('SELECT image_url FROM cars_images WHERE car_id = :car_id LIMIT 1')
        image_result = db.session.execute(image_sql, {'car_id': car['id']}).fetchone()
        car['image_url'] = image_result._mapping['image_url'] if image_result else None

        # 直接用 price_map 查價格
        car['price'] = price_map.get(car['car_level'], None)
        cars_list.append(car)
    
    return jsonify(cars_list)



@bp.route('/api/cars/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    # 獲取車輛基本資訊
    car_sql = text('SELECT * FROM cars WHERE id = :car_id')
    car_result = db.session.execute(car_sql, {'car_id': car_id}).fetchone()

    if not car_result:
        abort(404, description="Car not found")

    car = dict(car_result._mapping)  # 將結果轉換為字典

    # 獲取車輛圖片
    images_sql = text('SELECT image_url FROM cars_images WHERE car_id = :car_id')
    images_result = db.session.execute(images_sql, {'car_id': car_id}).fetchall()
    car['images'] = [row._mapping['image_url'] for row in images_result]

    # 查詢價格
    price_sql = text('SELECT price FROM prices WHERE level = :level AND type = "normal" LIMIT 1')
    price_result = db.session.execute(price_sql, {'level': car['car_level']}).fetchone()
    car['price'] = float(price_result[0]) if price_result else None

    return jsonify(car)


@bp.route('/api/cars/popular', methods=['GET'])
def get_popular_cars():
        # 先查所有價格，建立 level-price 對照表
        prices_sql = text('SELECT level, price FROM prices WHERE type = "normal"')
        prices_result = db.session.execute(prices_sql).fetchall()
        price_map = {row.level: row.price for row in prices_result}

        sql = text("""
    SELECT c.id, c.name, c.brand, c.year, c.body, c.seats, c.doors,
                 c.luggage_capacity, c.fuel_type, c.engine, c.transmission,
                 c.drive_type, c.mileage, c.fuel_economy, c.exterior_color,
                 c.interior_color, c.car_level
    FROM popular_cars pc
    JOIN cars c ON pc.car_id = c.id
    ORDER BY pc.sort_order ASC
        """)
        result = db.session.execute(sql)

        cars_list = []
        for row in result:
                car = dict(row._mapping)
                # 只取第一張圖片
                image_sql = text('SELECT image_url FROM cars_images WHERE car_id = :car_id LIMIT 1')
                image_result = db.session.execute(image_sql, {'car_id': car['id']}).fetchone()
                car['image_url'] = image_result._mapping['image_url'] if image_result else None
                # 加入價格
                car['price'] = price_map.get(car['car_level'], None)
                cars_list.append(car)
    
        return jsonify(cars_list)