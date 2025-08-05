from app.controllers import bp
from flask import render_template,request,redirect, url_for, flash
from app import db
from sqlalchemy import text
from app.services.s3_service import S3Service
from app.utils.role_decorators import role_required
from app.models.car_images import CarImages
from flask_login import current_user


@bp.route('/admin')
@role_required(['admin', 'superadmin']) 
def admin_index():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/index.html', cars=cars)


@bp.route('/admin/cars')
@role_required(['admin', 'superadmin']) 
def admin_cars():
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/cars.html', cars=cars)

@bp.route('/admin/edit_car/<int:car_id>', methods=['GET', 'POST'])
@role_required(['admin', 'superadmin']) 
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
@role_required(['admin', 'superadmin']) 
def admin_view_car(car_id):
    query = text('SELECT * FROM cars WHERE id = :car_id')
    car = db.session.execute(query, {'car_id': car_id}).fetchone()
    return render_template('admin/view_car.html', car=car)

@bp.route('/admin/upload', methods=['GET', 'POST'])
@role_required(['admin', 'superadmin'])
def admin_upload():
    if request.method == 'POST':
        if 'file' not in request.files or 'carId' not in request.form:
            flash('請選擇檔案並提供車輛 ID')
            return redirect(request.url)

        file = request.files['file']
        car_id = request.form.get('carId')  # 從表單獲取 car_id
        folder_name = request.form.get('folderName')  # 從表單獲取資料夾名稱

        if not car_id.isdigit():
            flash('車輛 ID 必須是有效的數字')
            return redirect(request.url)

        car_id = int(car_id)  # 將 car_id 轉換為整數

        # 確保 car_id 存在於 Car 表中
        sql = text("SELECT * FROM cars WHERE id = :car_id")
        result = db.session.execute(sql, {"car_id": car_id})
        car = result.fetchone()
        if not car:
            flash('提供的車輛 ID 無效，請選擇有效的車輛')
            return redirect(request.url)
        
        s3_service = S3Service()

        if not s3_service.allowed_file(file.filename):
            flash('只允許上傳圖片格式 (png, jpg, jpeg, gif)')
            return redirect(request.url)

        # 直接將 folder_name 傳給 S3Service，讓它處理預設值邏輯
        file_url = s3_service.upload_file(file, file.filename, folder_name)

        if file_url:
            # 儲存到資料庫
            new_image = CarImages(
                car_id=car.id,  # 使用 Car 表的 ID
                image_url=file_url,
                created_by=current_user.username  # 使用 Flask-Login 的 current_user
            )
            db.session.add(new_image)
            db.session.commit()

            flash(f'圖片上傳成功，車輛 ID: {car.id}，資料夾名稱: {folder_name}')
        else:
            flash('圖片上傳失敗')

        return redirect(url_for('controller.admin_upload'))

    # 查詢所有車輛資料並傳遞到模板
    sql = text("SELECT * FROM cars")
    result = db.session.execute(sql)
    cars = [row for row in result]
    return render_template('admin/upload.html', cars=cars)


@bp.route('/admin/user_list')
@role_required(['superadmin']) 
def user_list():
    sql = text("SELECT username, email, role FROM users")
    result = db.session.execute(sql)
    users = [row for row in result]
    return render_template('admin/user_list.html', users=users)