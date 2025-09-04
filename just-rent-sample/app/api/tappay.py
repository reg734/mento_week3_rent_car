from flask import jsonify, request, current_app
from app.api import bp


@bp.route('/api/tappay/config', methods=['GET'])
def get_tappay_config():
    """
    提供 TapPay 前端初始化配置
    只在需要時提供憑證，增加安全性
    """
    try:
  # CSRF Token 會自動被 Flask-WTF 驗證
  # 如果需要額外檢查可以加入：
        if not request.is_json and request.method == 'POST':
            return jsonify({
                'success': False,
                'message': 'Invalid request format'
            }), 400

        # 檢查必要的配置是否存在
        app_id = current_app.config.get('TAPPAY_APP_ID')
        app_key = current_app.config.get('TAPPAY_APP_KEY')

        if not app_id or not app_key:
            return jsonify({
                'success': False,
                'message': 'TapPay configuration not found'
            }), 500

        # 返回配置
        config = {
            'success': True,
            'app_id': app_id,
            'app_key': app_key,
            'environment': 'sandbox' if current_app.config.get('TAPPAY_SANDBOX', True) else 'production',
            'merchant_id': current_app.config.get('TAPPAY_MERCHANT_ID', '')
        }

        return jsonify(config)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
      
@bp.route('/api/tappay/status', methods=['GET'])
def get_tappay_status():
    """
    檢查 TapPay 配置狀態（除錯用）
    """
    try:
        status = {
            'success': True,
            'configured': bool(
                current_app.config.get('TAPPAY_APP_ID') and
                current_app.config.get('TAPPAY_APP_KEY')
            ),
            'environment': 'sandbox' if current_app.config.get('TAPPAY_SANDBOX', True) else 'production',
            'app_id_present': bool(current_app.config.get('TAPPAY_APP_ID')),
            'app_key_present': bool(current_app.config.get('TAPPAY_APP_KEY'))
        }

        return jsonify(status)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500