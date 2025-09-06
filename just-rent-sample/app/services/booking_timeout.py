"""
預訂逾期處理服務
處理 3 分鐘內未付款的預訂自動取消
"""

from app import db
from app.models import Booking, Car
from app.models.orders import Order
from datetime import datetime, timezone, timedelta
import threading
import time
import logging

logger = logging.getLogger(__name__)

class BookingTimeoutService:
    """預訂逾期處理服務"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.thread = None
        
    def init_app(self, app):
        """初始化 Flask 應用"""
        self.app = app
        
    def start(self):
        """啟動逾期檢查服務"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_timeout_checker, daemon=True)
            self.thread.start()
            logger.info("預訂逾期檢查服務已啟動")
    
    def stop(self):
        """停止逾期檢查服務"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("預訂逾期檢查服務已停止")
    
    def _run_timeout_checker(self):
        """運行逾期檢查循環"""
        while self.running:
            try:
                with self.app.app_context():
                    self._check_expired_bookings()
                time.sleep(30)  # 每 30 秒檢查一次
            except Exception as e:
                logger.error(f"預訂逾期檢查出錯: {str(e)}")
                time.sleep(60)  # 出錯時等待 60 秒後重試
    
    def _check_expired_bookings(self):
        """檢查並處理逾期的預訂"""
        # 設定台灣時區
        taiwan_timezone = timezone(timedelta(hours=8))
        now = datetime.now(taiwan_timezone)
        
        # 計算 3 分鐘前的時間
        timeout_threshold = now - timedelta(minutes=3)
        
        # 查詢逾期的預訂 (pending 狀態且超過 3 分鐘)
        expired_bookings = db.session.query(Booking).join(
            Order, Booking.id == Order.booking_id
        ).filter(
            Booking.booking_status == 'pending',
            Order.payment_status == 'pending',
            Booking.created_at < timeout_threshold
        ).all()
        
        if not expired_bookings:
            return
        
        logger.info(f"發現 {len(expired_bookings)} 個逾期預訂")
        
        for booking in expired_bookings:
            try:
                self._cancel_expired_booking(booking)
            except Exception as e:
                logger.error(f"取消逾期預訂 {booking.id} 時發生錯誤: {str(e)}")
    
    def _cancel_expired_booking(self, booking):
        """取消單個逾期預訂"""
        taiwan_timezone = timezone(timedelta(hours=8))
        now = datetime.now(taiwan_timezone)
        
        # 重新檢查 Order 狀態，防止競爭條件
        order = Order.query.filter_by(booking_id=booking.id).first()
        if order and order.payment_status == 'paid':
            # 如果付款已完成，不要取消訂單
            logger.warning(f"跳過取消訂單 {booking.id}：付款已完成 (payment_status=paid)")
            return
        
        # 重新檢查 Booking 狀態，防止競爭條件
        fresh_booking = Booking.query.get(booking.id)
        if fresh_booking and fresh_booking.booking_status != 'pending':
            # 如果訂單狀態已不是 pending，不要取消訂單
            logger.warning(f"跳過取消訂單 {booking.id}：狀態已變更為 {fresh_booking.booking_status}")
            return
        
        # 更新 Booking 狀態
        booking.booking_status = 'cancelled'
        
        # 更新 Order 狀態
        if order:
            order.payment_status = 'expired'
        
        # 釋放車輛
        car = Car.query.get(booking.car_id)
        if car:
            car.rental_status = 'available'
        
        db.session.commit()
        
        logger.info(f"已取消逾期預訂: Booking {booking.id}, Car {booking.car_id} 已釋放")
        
    def cancel_expired_booking_manually(self, booking_id):
        """手動取消逾期預訂 (用於測試)"""
        try:
            booking = Booking.query.get(booking_id)
            if booking and booking.booking_status == 'pending':
                self._cancel_expired_booking(booking)
                return True
            return False
        except Exception as e:
            logger.error(f"手動取消預訂失敗: {str(e)}")
            db.session.rollback()
            return False

# 全域服務實例
timeout_service = BookingTimeoutService()