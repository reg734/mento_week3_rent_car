from app.controllers import bp
from flask import render_template, redirect ,request, url_for
from flask_login import login_user, current_user, login_required




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
    return render_template('/account/account-orders.html', title='My Orders')

@bp.route('/account/favorite')
@login_required
def favorite():
    from app.models import MyFavorites, Car
    from app import db
    
    # 取得收藏車輛
    favorite_cars_query = db.session.query(Car).join(
        MyFavorites,
        (MyFavorites.car_id == Car.id) & 
        (MyFavorites.user_id == current_user.id)
    ).all()
    
    # 準備結果
    favorite_cars = []
    for car in favorite_cars_query:
        # 使用關聯取得圖片（car.images 是由 backref 產生的）
        image_url = car.images[0].image_url if car.images else '/static/images/default-car.jpg'
        
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
            'daily_rate': getattr(car, 'daily_rate', 265)
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



