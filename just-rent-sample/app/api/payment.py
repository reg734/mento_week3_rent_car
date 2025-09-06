from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from app.api import bp
from app.models import Car, Booking
from app.models.orders import Order
from app import db
from datetime import datetime, timezone, timedelta
import requests
import time

@bp.route('/api/payments/process', methods=['POST'])
@login_required
def process_payment():
    """
    處理 TapPay 付款請求 - 簡化測試版本
    """
    try:
        # 取得請求資料
        data = request.get_json()

        # 驗證必要欄位
        if not data or 'prime' not in data:
            return jsonify({
                'success': False,
                'message': '缺少付款憑證'
            }), 400

        prime = data.get('prime')
        amount = int(data.get('amount', 10))  # 預設測試金額
        booking_id = data.get('booking_id')
        order_id = data.get('order_id')
        car_id = data.get('car_id')
        
        # 驗證預訂資訊
        if not booking_id or not order_id or not car_id:
            return jsonify({
                'success': False,
                'message': '缺少預訂資訊'
            }), 400
        # 使用測試 Merchant ID
        merchant_id = current_app.config.get('TAPPAY_MERCHANT_ID')
        if merchant_id == '您的商店編號' or not merchant_id:
            merchant_id = 'GlobalTesting_CTBC'  # 使用測試 ID
            print(f"使用測試 Merchant ID: {merchant_id}")

        # 準備 TapPay API 請求 - 簡化版本
        tappay_data = {
            "prime": prime,
            "partner_key": current_app.config.get('TAPPAY_PARTNER_KEY', 'test'),
            "merchant_id": merchant_id,
            "amount": amount,
            "details":"TapPay Test",
            "currency": "TWD",
            "details": "JustRent Test Payment",
            "cardholder": {
                  "phone_number": "+886923456789",  # 測試用電話
                  "name": "Test User",              # 測試用姓名
                  "email": "test@example.com"       # 測試用 email
              }
        }

        # 沙盒 API URL
        api_url = 'https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime'

        # 發送請求到 TapPay
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': current_app.config.get('TAPPAY_PARTNER_KEY', 'test')
        }

        response = requests.post(api_url,
                                json=tappay_data,
                                headers=headers,
                                timeout=30)
        
        # 解析 TapPay 回應
        tappay_response = response.json()

        # 檢查付款結果
        if tappay_response.get('status') == 0:
            # 付款成功 - 更新資料庫狀態
            try:
                transaction_id = tappay_response.get('rec_trade_id', 'TEST-' + str(int(time.time())))
                
                # 設定台灣時區 (UTC+8)
                taiwan_timezone = timezone(timedelta(hours=8))
                taiwan_now = datetime.now(taiwan_timezone)
                
                # 使用行級鎖確保原子性（避免雙重事務）
                # 1. 更新 Order 狀態 - 先更新付款狀態防止競爭條件
                order = Order.query.with_for_update().filter_by(id=order_id).first()
                if not order:
                    raise Exception(f"Order {order_id} not found")
                
                if order.payment_status == 'paid':
                    # 避免重複處理
                    print(f"Order {order_id} 已經是 paid 狀態，跳過重複處理")
                    return jsonify({
                        'success': True,
                        'message': '付款已完成',
                        'order_number': f'ORDER-{order_id}',
                        'transaction_id': order.transaction_id,
                        'amount': float(order.amount) if order.amount else 0
                    })
                
                order.payment_status = 'paid'
                order.transaction_id = transaction_id
                order.paid_at = taiwan_now
                order.payment_method = 'TapPay'
                
                # 2. 更新 Booking 狀態
                booking = Booking.query.with_for_update().filter_by(id=booking_id).first()
                if not booking:
                    raise Exception(f"Booking {booking_id} not found")
                
                booking.booking_status = 'confirmed'
                
                # 3. 更新 Car 狀態
                car = Car.query.with_for_update().filter_by(id=car_id).first()
                if car:
                    car.rental_status = 'rented'
                
                # 提交所有變更
                db.session.commit()
                
                print(f"=== 付款成功，狀態已更新 ===")
                print(f"Transaction ID: {transaction_id}")
                print(f"Taiwan Time: {taiwan_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"Order {order_id}: payment_status = paid, paid_at = {taiwan_now}")
                print(f"Booking {booking_id}: booking_status = confirmed")
                print(f"Car {car_id}: rental_status = rented")
                
                return jsonify({
                    'success': True,
                    'message': '付款成功',
                    'transaction_id': transaction_id,
                    'order_number': transaction_id,
                    'booking_id': booking_id,
                    'order_id': order_id
                })
                
            except Exception as db_error:
                # 資料庫更新失敗，需要回滾
                db.session.rollback()
                print(f"資料庫更新失敗: {str(db_error)}")
                
                return jsonify({
                    'success': False,
                    'message': '付款成功但系統更新失敗，請聯繫客服',
                    'transaction_id': transaction_id
                }), 500
        else:
            # 付款失敗 - 回傳更詳細的錯誤資訊
            error_msg = tappay_response.get('msg', '付款處理失敗')
            print(f"Payment failed: {error_msg}")
            print(f"Full response: {tappay_response}")

            return jsonify({
                'success': False,
                'message': error_msg,
                'status': tappay_response.get('status'),
                'details': str(tappay_response)  # 暫時回傳完整錯誤供除錯
            }), 400
    except Exception as e:
        current_app.logger.error(f'Payment error: {str(e)}')
        return jsonify({
            'success': False,
            'message': '系統錯誤'
        }), 500