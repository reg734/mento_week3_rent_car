from app.controllers import bp
from flask import render_template, redirect ,request, url_for
from flask_login import login_required, login_user




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
    return render_template('/account/account-favorite.html', title='My Favorite Cars')

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



