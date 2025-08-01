from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 未登入或權限不足：導向登入頁面
            if not current_user.is_authenticated or current_user.role not in roles:
                if not current_user.is_authenticated:
                    flash('請先登入', 'warning')
                else:
                    flash('權限不足，需要管理員權限', 'error')
                return redirect(url_for('controller.admin_login'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator