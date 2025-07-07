from app.controllers import bp
from flask import render_template
from app import db
from sqlalchemy import text

@bp.route('/admin')
def admin_index():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/index.html', cars=cars)


@bp.route('/admin/cars')
def admin_cars():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/cars.html', cars=cars)