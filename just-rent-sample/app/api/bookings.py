from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.models import Car, Location, Booking, Price, User
from app import db
from datetime import datetime
from dateutil import parser
import math
from sqlalchemy import text

@bp.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    """取得訂單列表 - 管理員可看所有訂單，一般用戶只能看自己的訂單"""
    
    # 建立 Location 表的別名
    pickup_location = Location.__table__.alias('pickup_loc')
    dropoff_location = Location.__table__.alias('dropoff_loc')
    
    # 基礎查詢
    query = db.session.query(
        Booking,
        Car.name.label('car_name'),
        User.username.label('user_name'),
        pickup_location.c.name.label('pickup_location'),
        dropoff_location.c.name.label('dropoff_location')
    ).join(
        Car, Booking.car_id == Car.id
    ).join(
        User, Booking.user_id == User.id
    ).join(
        pickup_location, Booking.pick_up_location_id == pickup_location.c.id
    ).join(
        dropoff_location, Booking.drop_off_location_id == dropoff_location.c.id
    )
    
    # 根據權限過濾資料
    if not current_user.is_admin():
        # 一般用戶只能看自己的訂單
        query = query.filter(Booking.user_id == current_user.id)
    
    # 執行查詢
    results = query.order_by(Booking.pick_up_time.desc()).all()
    
    # 整理資料
    bookings_list = []
    for booking, car_name, user_name, pickup_location, dropoff_location in results:
        bookings_list.append({
            'id': booking.id,
            'user_id': booking.user_id,
            'user_name': user_name,
            'car_id': booking.car_id,
            'car_name': car_name,
            'pickup_location': pickup_location,
            'dropoff_location': dropoff_location,
            'pick_up_time': booking.pick_up_time.isoformat() if booking.pick_up_time else None,
            'return_time': booking.return_time.isoformat() if booking.return_time else None,
            'status': booking.status
        })
    
    return jsonify({
        'success': True,
        'bookings': bookings_list,
        'is_admin': current_user.is_admin()
    })

@bp.route('/api/bookings/available-cars', methods=['GET'])
def get_available_cars():
    # 從查詢參數取得資料
    car_type = request.args.get('car_type')
    pickup_location = request.args.get('pickup_location')
    dropoff_location = request.args.get('dropoff_location')
    pickup_date = request.args.get('pickup_date')
    pickup_time = request.args.get('pickup_time')
    return_date = request.args.get('return_date')
    return_time = request.args.get('return_time')
    
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
        "%Y-%m-%d %H:%M",
        "%B %d, %Y %H:%M",
        "%m/%d/%Y %H:%M",
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
            if pickup_date:
                pickup_dt = parser.parse(f"{pickup_date} {pickup_time}")
            if return_date:
                return_dt = parser.parse(f"{return_date} {return_time}")
        except:
            pass
    
    # 時間判斷（改為 JSON 錯誤回應）
    now = datetime.now()
    if pickup_dt and pickup_dt < now:
        return jsonify({
            'status': 'error',
            'message': '取車時間不可早於現在時間，請重新選取。'
        }), 400
    
    if pickup_dt and return_dt and return_dt < pickup_dt:
        return jsonify({
            'status': 'error',
            'message': '還車時間不可早於取車時間，請重新選取。'
        }), 400
    
    # 建立英文到中文的車型映射
    body_type_mapping = {
        'Hatchback': '掀背車',
        'Sedan': '轎車',
        'SUV': '休旅車'
    }
    
    # 查詢可用車輛
    car_query = Car.query
    if car_type and car_type != 'All':
        chinese_body = body_type_mapping.get(car_type, car_type)
        car_query = car_query.filter_by(body=chinese_body)
    
    # 取得所有符合條件的車輛
    all_cars = car_query.all()
    available_cars = []
    
    # 只有當日期時間都有效時才檢查訂單重疊
    if pickup_dt and return_dt and all_cars:
        for car in all_cars:
            overlap = Booking.query.filter(
                Booking.car_id == car.id,
                Booking.pick_up_time < return_dt,
                Booking.return_time > pickup_dt,
                Booking.status != 'cancelled'
            ).first()
            if not overlap:
                available_cars.append(car)
    else:
        available_cars = all_cars
    
    # 為每個車輛加入價格資訊（需要轉成字典格式）
    cars_list = []
    for car in available_cars:
        price_info = Price.query.filter_by(level=car.car_level, type='normal').first()
        price = float(price_info.price) if price_info else 0
        
        # 轉換為字典
        cars_list.append({
            'id': car.id,
            'name': car.name,
            'body': car.body,
            'seats': car.seats,
            'doors': car.doors,
            'luggage_capacity': car.luggage_capacity,
            'car_level': car.car_level,
            'price': price
        })
    
    # 計算租賃天數
    rental_days = 1
    if pickup_dt and return_dt:
        time_diff = return_dt - pickup_dt
        total_hours = time_diff.total_seconds() / 3600
        rental_days = max(1, math.ceil(total_hours / 24))
    
    # 處理無車輛的情況
    if len(cars_list) == 0:
        message = '目前沒有符合您選擇車型的車輛' if len(all_cars) == 0 else f'您選擇的時段沒有可用車輛'
        return jsonify({
            'status': 'warning',
            'message': message,
            'cars': [],
            'rental_days': rental_days
        })
    
    return jsonify({
        'status': 'success',
        'cars': cars_list,  # 使用轉換後的列表
        'rental_days': rental_days
    })

@bp.route('/api/bookings', methods=['POST'])
@login_required
def create_booking():
    """建立新的訂單"""
    data = request.json
    
    # 取得表單資料
    car_id = data.get('car_id')
    pickup_location = data.get('pickup_location')
    dropoff_location = data.get('dropoff_location')
    pickup_datetime = data.get('pickup_datetime')
    return_datetime = data.get('return_datetime')
    
    # 除錯：印出接收到的資料
    print(f"=== API 接收到的資料 ===")
    print(f"data: {data}")
    print(f"pickup_location: '{pickup_location}'")
    print(f"dropoff_location: '{dropoff_location}'")
    print(f"pickup_datetime: '{pickup_datetime}'")
    print(f"return_datetime: '{return_datetime}'")
    
    try:
        # 解析日期時間
        pickup_dt = datetime.fromisoformat(pickup_datetime.replace('Z', '+00:00'))
        return_dt = datetime.fromisoformat(return_datetime.replace('Z', '+00:00'))
        
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
            'taipei': '台北站',
            'taichung': '台中站',
            'kaohsiung': '高雄站'
        }
        
        # 取得標準化的地點名稱
        pickup_name = location_mapping.get(pickup_location, pickup_location)
        dropoff_name = location_mapping.get(dropoff_location, dropoff_location)
        
        # 除錯：印出地點映射結果
        print(f"=== 地點映射結果 ===")
        print(f"原始 pickup_location: '{pickup_location}' -> 映射後: '{pickup_name}'")
        print(f"原始 dropoff_location: '{dropoff_location}' -> 映射後: '{dropoff_name}'")
        
        # 查詢地點
        pickup_loc = Location.query.filter_by(name=pickup_name).first()
        dropoff_loc = Location.query.filter_by(name=dropoff_name).first()
        
        # 除錯：印出查詢結果
        print(f"=== 地點查詢結果 ===")
        print(f"pickup_loc: {pickup_loc} (id: {pickup_loc.id if pickup_loc else None})")
        print(f"dropoff_loc: {dropoff_loc} (id: {dropoff_loc.id if dropoff_loc else None})")
        
        if not pickup_loc or not dropoff_loc:
            error_msg = []
            if not pickup_loc:
                error_msg.append(f'找不到取車地點：{pickup_location}')
            if not dropoff_loc:
                error_msg.append(f'找不到還車地點：{dropoff_location}')
            error_msg.append('請輸入：台北站、台中站或高雄站')
            
            return jsonify({
                'status': 'error',
                'message': ' / '.join(error_msg)
            }), 400
        
        # 建立訂單
        booking = Booking(
            user_id=current_user.id,
            car_id=car_id,
            pick_up_location_id=pickup_loc.id,
            drop_off_location_id=dropoff_loc.id,
            pick_up_time=pickup_dt,
            return_time=return_dt,
            status='scheduled'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '訂單已成功建立！',
            'booking_id': booking.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'訂單建立失敗：{str(e)}'
        }), 500
    

@bp.route('/api/bookings/cancel/<int:order_id>', methods=['POST'])
@login_required
def api_cancel_order(order_id):
    # 檢查是否為管理員
    if current_user.is_admin():
        # 管理員可以取消任何訂單
        booking = Booking.query.get(order_id)
        if not booking:
            return jsonify({'success': False, 'message': '找不到此訂單'})
    else:
        # 一般用戶只能取消自己的訂單
        booking = Booking.query.filter_by(id=order_id, user_id=current_user.id).first()
        if not booking:
            return jsonify({'success': False, 'message': '找不到此訂單或無權限取消'})

    if booking.status == 'cancelled':
        return jsonify({'success': False, 'message': '訂單已取消'})

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'success': True, 'message': '訂單已成功取消'})