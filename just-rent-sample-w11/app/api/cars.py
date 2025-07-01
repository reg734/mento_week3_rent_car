from app import db
from app.api import bp
from flask import jsonify
from sqlalchemy import text
from flask import Blueprint,request

@bp.route('/api/cars', methods=['GET'])
def get_cars():
    sql = text('SELECT id, name, seat, door, body, displacement, car_type, seat_number, door_number, car_length, wheelbase, power_type, brand, model FROM cars')
    result = db.session.execute(sql)

    cars_list = [dict(row._mapping) for row in result]

    return jsonify(cars_list)