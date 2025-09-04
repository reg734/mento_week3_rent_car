from flask import request, jsonify, current_app
from app.api import bp
import requests
import time

@bp.route('/api/payments/process', methods=['POST'])
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
            # 付款成功
            return jsonify({
                'success': True,
                'message': '付款成功',
                'order_number': tappay_response.get('rec_trade_id', 'TEST-' + str(int(time.time())))
            })
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