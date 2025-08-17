from app.controllers import bp
from flask import render_template, redirect ,request, url_for, flash
from flask_login import login_user, current_user, login_required
from app.models import MyFavorite, Car ,Location, Booking, Price
from app import db


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
@login_required
def dashboard():
    return render_template('/account/account-dashboard.html', title='My Account')

@bp.route('/account/profile')
@login_required
def profile():
    return render_template('/account/account-profile.html', title='My Profile')

@bp.route('/account/orders')
@login_required
def orders():
    # 建立 Location 表的別名，因為需要 JOIN 兩次
    pickup_location = Location.__table__.alias('pickup_loc')
    dropoff_location = Location.__table__.alias('dropoff_loc')
    
    # 查詢該使用者的所有訂單，並 join 車輛和兩個地點
    orders = db.session.query(
        Booking,
        Car.name.label('car_name'),
        pickup_location.c.name.label('pickup_location'),
        dropoff_location.c.name.label('dropoff_location')
    ).join(
        Car, Booking.car_id == Car.id
    ).join(
        pickup_location, Booking.pick_up_location_id == pickup_location.c.id
    ).join(
        dropoff_location, Booking.drop_off_location_id == dropoff_location.c.id
    ).filter(
        Booking.user_id == current_user.id
    ).all()

    # 整理資料給 template
    order_list = []
    for booking, car_name, pickup_location, dropoff_location in orders:
        order_list.append({
            'id': booking.id,
            'car_name': car_name,
            'pickup_location': pickup_location,
            'dropoff_location': dropoff_location,
            'pick_up_time': booking.pick_up_time,
            'return_time': booking.return_time,
            'status': booking.status
        })

    return render_template('/account/account-orders.html', title='My Orders', orders=order_list)

@bp.route('/account/orders/cancel/<int:order_id>')
@login_required
def cancel_order(order_id):
    booking = Booking.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not booking:
        flash('找不到此訂單或無權限取消', 'error')
        return redirect(url_for('controller.orders'))
    if booking.status == 'cancelled':
        flash('訂單已取消', 'warning')
        return redirect(url_for('controller.orders'))
    booking.status = 'cancelled'
    db.session.commit()
    flash('訂單已成功取消', 'success')
    return redirect(url_for('controller.orders'))


@bp.route('/account/favorite')
@login_required
def favorite():
    
    # 取得收藏車輛
    favorite_cars_query = db.session.query(Car).join(
        MyFavorite,
        (MyFavorite.car_id == Car.id) & 
        (MyFavorite.user_id == current_user.id)
    ).all()
    
    # 準備結果
    favorite_cars = []
    for car in favorite_cars_query:
        # 使用關聯取得圖片（car.images 是由 backref 產生的）
        image_url = car.images[0].image_url if car.images else '/static/images/default-car.jpg'
        
        # 查詢車輛的價格
        price_info = Price.query.filter_by(level=car.car_level, type='normal').first()
        daily_rate = float(price_info.price) if price_info else 265
        
        favorite_cars.append({
            'id': car.id,
            'name': car.name,
            'image_url': image_url,
            'seats': car.seats,
            'luggage_capacity': car.luggage_capacity,
            'doors': car.doors,
            'fuel_type': getattr(car, 'fuel_type', 'Petrol'),
            'year': getattr(car, 'year', 2000),
            'engine': getattr(car, 'engine', 3000),
            'drive_type': getattr(car, 'drive_type', '4x4'),
            'body': car.body,
            'daily_rate': daily_rate
        })
    
    return render_template('/account/account-favorite.html',
                         title='My Favorite Cars',
                         favorite_cars=favorite_cars)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 取得表單資料
        username = request.form.get('username')
        password = request.form.get('password')
        # 查詢使用者並驗證密碼（略）
        # 假設你有一個 User 模型和驗證方法
        from app.models import User  # 確保你有這個 import
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('controller.dashboard'))
        else:
            return render_template('login.html', title='Login', error='Invalid credentials')
    return render_template('login.html', title='Login')

@bp.route('/register')
def register():
    return render_template('register.html', title='Register')

@bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('controller.home'))



