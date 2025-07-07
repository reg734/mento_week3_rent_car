from app.controllers import bp
from flask import render_template


@bp.route('/admin')
def admin_index():
    return render_template('admin/index.html')

