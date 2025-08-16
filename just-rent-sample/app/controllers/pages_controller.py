from app.controllers import bp
from flask import render_template, redirect ,request, url_for, flash
from flask_login import login_user, current_user, login_required
from app.models import MyFavorite, Car ,Location, Booking, Price
from app import db
from datetime import datetime
from dateutil import parser




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

@bp.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        car_type = request.form.get('Car_Type')
        pickup_location = request.form.get('PickupLocation')
        dropoff_location = request.form.get('DropoffLocation')
        pickup_date = request.form.get('Pick Up Date')
        pickup_time = request.form.get('Pick Up Time')
        return_date = request.form.get('Collection Date')
        return_time = request.form.get('Collection Time')

        # 組合時間
        pickup_dt = None
        return_dt = None
        
        # 處理時間預設值
        if pickup_time in ['Select time', 'Time', None, '']:
            pickup_time = '00:00'
        if return_time in ['Select time', 'Time', None, '']:
            return_time = '00:00'
        
        # 嘗試多種日期格式
        date_formats = [
            "%Y-%m-%d %H:%M",           # 2025-08-16 10:00
            "%B %d, %Y %H:%M",          # August 16, 2025 10:00
            "%m/%d/%Y %H:%M",           # 08/16/2025 10:00
        ]
        
        for fmt in date_formats:
            try:
                pickup_dt = datetime.strptime(f"{pickup_date} {pickup_time}", fmt)
                return_dt = datetime.strptime(f"{return_date} {return_time}", fmt)
                break
            except:
                continue
        
        # 如果所有格式都失敗，嘗試更靈活的解析
        if not pickup_dt or not return_dt:
            try:
                # 處理 "August 16, 2025" 格式
                if pickup_date:
                    pickup_dt = parser.parse(f"{pickup_date} {pickup_time}")
                if return_date:
                    return_dt = parser.parse(f"{return_date} {return_time}")
            except:
                pass
        
        # Debug 輸出
        print(f"DEBUG - Parsed datetime:")
        print(f"  pickup_date: {pickup_date}, pickup_time: {pickup_time}")
        print(f"  return_date: {return_date}, return_time: {return_time}")
        print(f"  pickup_dt: {pickup_dt}")
        print(f"  return_dt: {return_dt}")

        # 時間判斷
        now = datetime.now()
        if pickup_dt and pickup_dt < now:
            flash('取車時間不可早於現在時間，請重新選取。', 'error')
            return redirect(url_for('controller.booking'))

        if pickup_dt and return_dt and return_dt < pickup_dt:
            flash('還車時間不可早於取車時間，請重新選取。', 'error')
            return redirect(url_for('controller.booking'))
        
         # 建立英文到中文的車型映射
        body_type_mapping = {
            'Hatchback': '掀背車',
            'Sedan': '轎車',
            'SUV': 'SUV'
        }
        
        # 查詢可用車輛
        car_query = Car.query
        if car_type and car_type != 'All':
            # 將英文車型轉換為中文（如果在映射中）
            chinese_body = body_type_mapping.get(car_type, car_type)
            car_query = car_query.filter_by(body=chinese_body)
            print(f"DEBUG - Filtering by body type: {chinese_body}")
        
        # 取得所有符合條件的車輛
        all_cars = car_query.all()
        available_cars = []
        print(f"DEBUG - Total cars found: {len(all_cars)}")
        
        # 只有當日期時間都有效時才檢查訂單重疊
        if pickup_dt and return_dt and all_cars:
            for car in all_cars:
                # 檢查是否有重疊訂單
                overlap = Booking.query.filter(
                    Booking.car_id == car.id,
                    Booking.pick_up_time < return_dt,
                    Booking.return_time > pickup_dt
                ).first()
                if not overlap:
                    available_cars.append(car)
        else:
            # 如果日期無效或沒有指定，顯示所有符合車型的車輛
            available_cars = all_cars
        
        # 為每個車輛加入價格資訊
        for car in available_cars:
            # 根據 car_level 查詢對應的價格
            price_info = Price.query.filter_by(level=car.car_level, type='normal').first()
            if price_info:
                car.price = float(price_info.price)
            else:
                car.price = 0  # 預設價格
        
        # 為了除錯：如果沒有車輛，至少印出訊息
        print(f"DEBUG: Found {len(available_cars)} available cars")
        if len(available_cars) == 0:
            print("DEBUG: No cars available - checking why:")
            print(f"  - all_cars count: {len(all_cars)}")
            print(f"  - pickup_dt: {pickup_dt}")
            print(f"  - return_dt: {return_dt}")
            if len(all_cars) == 0:
                print("  - No cars in database matching criteria")
                # 檢查資料庫是否有任何車輛
                total_cars = Car.query.count()
                print(f"  - Total cars in database: {total_cars}")
            
            # 顯示 flash 訊息
            if len(all_cars) == 0:
                flash('目前沒有符合您選擇車型的車輛，請選擇其他車型或選擇 "All" 查看所有車輛。', 'warning')
            else:
                flash(f'您選擇的時段沒有可用車輛（共 {len(all_cars)} 輛車已被預訂），請選擇其他時間。', 'warning')

        rental_days = 1  # 預設1天
        if pickup_dt and return_dt:
            time_diff = return_dt - pickup_dt
            total_hours = time_diff.total_seconds() / 3600
            # 超過24小時就算2天，超過48小時算3天，以此類推
            import math
            rental_days = max(1, math.ceil(total_hours / 24))

        # 回傳 booking.html 並顯示可用車輛
        # 只有當有可用車輛時才顯示光箱
        show_modal = len(available_cars) > 0
        return render_template('booking.html', title='Booking', available_cars=available_cars,
                              pickup_location=pickup_location, dropoff_location=dropoff_location,
                              pickup_date=pickup_date, pickup_time=pickup_time,
                              return_date=return_date, return_time=return_time,
                              pickup_dt=pickup_dt, return_dt=return_dt,
                              rental_days=rental_days, show_modal=show_modal)
    else:
        # GET 請求時顯示空的預訂表單
        return render_template('booking.html', title='Booking', 
                             available_cars=[],
                             pickup_location='',
                             dropoff_location='',
                             pickup_date='',
                             pickup_time='',
                             return_date='',
                             return_time='')


@bp.route('/booking/confirm', methods=['POST'])
@login_required
def booking_confirm():
    # 取得表單資料
    car_id = request.form.get('car_id')
    pickup_location = request.form.get('pickup_location')
    dropoff_location = request.form.get('dropoff_location')
    pickup_date = request.form.get('pickup_date')
    pickup_time = request.form.get('pickup_time')
    return_date = request.form.get('return_date')
    return_time = request.form.get('return_time')
    
    # 除錯：印出收到的資料
    print(f"DEBUG - booking_confirm 收到的資料:")
    print(f"  car_id: {car_id}")
    print(f"  pickup_location: {pickup_location}")
    print(f"  dropoff_location: {dropoff_location}")
    print(f"  pickup_date: {pickup_date}")
    print(f"  pickup_time: {pickup_time}")
    print(f"  return_date: {return_date}")
    print(f"  return_time: {return_time}")
    print(f"  current_user.id: {current_user.id}")
    
    try:
        # 組合日期時間 - 支援多種日期格式
        from datetime import datetime
        
        def parse_datetime(date_str, time_str):
            """解析日期時間，支援多種格式"""
            print(f"DEBUG - 解析日期時間: date='{date_str}', time='{time_str}'")
            
            # 處理可能的日期格式
            date_formats = [
                "%Y-%m-%d",           # 2025-08-16
                "%B %d, %Y",          # August 16, 2025
                "%m/%d/%Y",           # 08/16/2025
                "%d/%m/%Y",           # 16/08/2025
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    # 如果 date_str 包含時間，先分離
                    date_only = date_str.split(' ')[0:3]  # 取前3部分如 "August 16, 2025"
                    if len(date_only) == 3:
                        date_only = ' '.join(date_only).rstrip(',')
                    else:
                        date_only = date_str.split(' ')[0]  # 只取第一部分
                    
                    parsed_date = datetime.strptime(date_only, fmt)
                    print(f"DEBUG - 成功解析日期: {date_only} -> {parsed_date}")
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                raise ValueError(f"無法解析日期格式: {date_str}")
            
            # 處理時間部分
            if not time_str or time_str == "Time":
                time_str = "00:00"
            
            try:
                time_obj = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                # 如果時間格式錯誤，使用 00:00
                time_obj = datetime.strptime("00:00", "%H:%M").time()
            
            # 合併日期和時間
            result = datetime.combine(parsed_date.date(), time_obj)
            print(f"DEBUG - 最終日期時間: {result}")
            return result
        
        pickup_dt = parse_datetime(pickup_date, pickup_time)
        return_dt = parse_datetime(return_date, return_time)
        
        
        # 建立地點映射表
        location_mapping = {
            '台北': '台北站',
            '台中': '台中站', 
            '高雄': '高雄站',
            'Taipei': '台北站',
            'Taichung': '台中站',
            'Kaohsiung': '高雄站',
            '台北站': '台北站',
            '台中站': '台中站',
            '高雄站': '高雄站',
            # 可以加入更多變體
            'taipei': '台北站',
            'taichung': '台中站',
            'kaohsiung': '高雄站'
        }
        
        # 取得標準化的地點名稱（忽略大小寫）
        pickup_name = location_mapping.get(pickup_location, None)
        if not pickup_name and pickup_location:
            # 嘗試小寫匹配
            pickup_name = location_mapping.get(pickup_location.lower(), pickup_location)
        
        dropoff_name = location_mapping.get(dropoff_location, None)
        if not dropoff_name and dropoff_location:
            # 嘗試小寫匹配
            dropoff_name = location_mapping.get(dropoff_location.lower(), dropoff_location)
        
        # 查詢地點
        pickup_loc = Location.query.filter_by(name=pickup_name).first() if pickup_name else None
        dropoff_loc = Location.query.filter_by(name=dropoff_name).first() if dropoff_name else None
        
        if not pickup_loc or not dropoff_loc:
            error_msg = []
            if not pickup_loc:
                error_msg.append(f'找不到取車地點：{pickup_location}')
            if not dropoff_loc:
                error_msg.append(f'找不到還車地點：{dropoff_location}')
            error_msg.append('請輸入：台北站、台中站或高雄站')
            
            flash(' / '.join(error_msg), 'error')
            return redirect(url_for('controller.booking'))
        
        # 建立訂單
        booking = Booking(
            user_id=current_user.id,
            car_id=car_id,
            pick_up_location_id=pickup_loc.id,
            drop_off_location_id=dropoff_loc.id,
            pick_up_time=pickup_dt,
            return_time=return_dt,
            status='confirmed'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # 重導向到訂單頁面或顯示成功訊息
        flash('訂單已成功建立！', 'success')
        return redirect(url_for('controller.orders'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'訂單建立失敗：{str(e)}', 'error')
        return redirect(url_for('controller.booking'))


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



