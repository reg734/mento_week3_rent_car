from app.api import bp
from app.models import Car
from flask import jsonify

@bp.route('/api/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    data = []

    for car in cars:
        data.append({
            "id": car.id,
            "name": car.name,
            "brand": car.brand,
            "year": car.year,
            "structure": {
                "body": car.body,
                "door": car.door,
                "door_number": car.door_number,
                "seat": car.seat,
                "seat_number": car.seat_number,
                "car_length": car.car_length,
                "wheelbase": car.wheelbase,
                "exterior_color": car.exterior_color,
                "interior_color": car.interior_color
            },
            "engine": {
                "engine": car.engine,
                "power_type": car.power_type,
                "fuel_economy": car.fuel_economy
            },
            "performance": {
                "transmission": car.transmission,
                "drive": car.drive
            },
            "misc": {
                "luggage": car.luggage,
                "mileage": car.mileage,
                "vehicle_type": car.vehicle_type
            }
        })
    
    return jsonify(data)
