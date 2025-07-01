from app.controllers import bp
from flask import render_template




@bp.route('/')
def home():
    return render_template('index.html', title='Home')

@bp.route('/cars')
def cars():
    return render_template('cars.html', title='Cars')

@bp.route('/cars/list')
def cars_list():
    return render_template('cars-list.html', title='Cars List')

@bp.route('/cars/<int:car_id>')
def car_detail(car_id):
    return render_template('car-single.html', title=f'Car #{car_id}', car_id=car_id)

@bp.route('/booking')
def booking():
    return render_template('booking.html', title='Booking')

@bp.route('/account/dashboard')
def dashboard():
    return render_template('account-dashboard.html', title='My Account')

@bp.route('/account/profile')
def profile():
    return render_template('account-profile.html', title='My Profile')

@bp.route('/account/orders')
def orders():
    return render_template('account-booking.html', title='My Orders')

@bp.route('/account/favorite')
def favorite():
    return render_template('account-favorite.html', title='My Favorite Cars')

@bp.route('/login')
def login():
    return render_template('login.html', title='Login')

@bp.route('/register')
def register():
    return render_template('register.html', title='Register')



