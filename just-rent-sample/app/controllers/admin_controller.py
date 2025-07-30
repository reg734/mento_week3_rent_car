from app.controllers import bp
from flask import render_template,request,redirect, url_for, flash
from app import db
from sqlalchemy import text
from app.services.s3_service import S3Service

@bp.route('/admin')
def admin_index():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/index.html', cars=cars)


@bp.route('/admin/cars')
def admin_cars():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/cars.html', cars=cars)

@bp.route('/admin/edit_car/<int:car_id>', methods=['GET', 'POST'])
def admin_edit_car(car_id):
    if request.method == 'POST':
        db.session.execute(text("""
            UPDATE cars SET
                name = :name,
                seat = :seat,
                door = :door,
                body = :body,
                seat_number = :seat_number,
                door_number = :door_number,
                car_length = :car_length,
                wheelbase = :wheelbase,
                power_type = :power_type,
                brand = :brand,
                displacement = :displacement,
                car_type = :car_type,
                model = :model
            WHERE id = :car_id
        """), {
            'name': request.form['name'],
            'seat': request.form['seat'],
            'door': request.form['door'],
            'body': request.form['body'],
            'seat_number': request.form['seat_number'],
            'door_number': request.form['door_number'],
            'car_length': request.form['car_length'],
            'wheelbase': request.form['wheelbase'],
            'power_type': request.form['power_type'],
            'brand': request.form['brand'],
            'displacement': request.form['displacement'],
            'car_type': request.form['car_type'],
            'model': request.form['model'],
            'car_id': car_id
        })

        db.session.commit()
        return redirect(url_for('controller.admin_index'))

    query = text('SELECT * FROM cars WHERE id = :car_id')
    car = db.session.execute(query, {'car_id': car_id}).fetchone()

    return render_template('admin/edit_car.html', car=car)

@bp.route('/admin/view_car/<int:car_id>')
def admin_view_car(car_id):
    query = text('SELECT * FROM cars WHERE id = :car_id')
    car = db.session.execute(query, {'car_id': car_id}).fetchone()


    return render_template('admin/view_car.html', car=car)


# 定義允許的圖片擴展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/admin/upload', methods=['GET', 'POST'])
def admin_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('請選擇要上傳的檔案')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('未選擇檔案')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('只允許上傳圖片(png, jpg, jpeg, gif)')
            return redirect(request.url)
        if file:
            # 使用 S3Service 上傳文件
            s3_service = S3Service()
            file_url = s3_service.upload_file(file, file.filename)
            if file_url:
                flash(f'檔案上傳成功: {file_url}')
            else:
                flash('檔案上傳失敗')
            return redirect(url_for('controller.admin_upload'))
    return render_template('admin/upload.html')