from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.users import User
from app.controllers import bp


@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_admin(): 
                login_user(user)
                flash('登入成功！', 'success')
                return redirect(url_for('controller.admin_index'))
            else:
                flash('權限不足，需要管理員權限', 'danger') 
        else:
            flash('無效的電子郵件或密碼', 'danger')
    return render_template('admin/login.html')

@bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('您已成功登出。', 'success')
    return redirect(url_for('controller.admin_login'))