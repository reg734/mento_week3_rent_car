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
        # 處理數值型欄位的輔助函數
        def get_numeric_value(value, default=None):
            if not value or value == 'None' or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        def get_int_value(value, default=None):
            if not value or value == 'None' or value == '':
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        db.session.execute(text("""
            UPDATE cars SET
                name = :name,
                seats = :seats,
                doors = :doors,
                body = :body,
                luggage_capacity = :luggage_capacity,
                fuel_type = :fuel_type,
                engine = :engine,
                transmission = :transmission,
                drive_type = :drive_type,
                mileage = :mileage,
                fuel_economy = :fuel_economy,
                exterior_color = :exterior_color,
                interior_color = :interior_color,
                brand = :brand,
                year = :year,
                daily_rate = :daily_rate
            WHERE id = :car_id
        """), {
            'name': request.form.get('name', ''),
            'seats': get_int_value(request.form.get('seats')),
            'doors': get_int_value(request.form.get('doors')),
            'body': request.form.get('body', ''),
            'luggage_capacity': get_int_value(request.form.get('luggage_capacity')),
            'fuel_type': request.form.get('fuel_type', ''),
            'engine': request.form.get('engine', ''),
            'transmission': request.form.get('transmission', ''),
            'drive_type': request.form.get('drive_type', '') if request.form.get('drive_type') != 'None' else '',
            'mileage': get_numeric_value(request.form.get('mileage'), 0),
            'fuel_economy': get_numeric_value(request.form.get('fuel_economy')),
            'exterior_color': request.form.get('exterior_color', ''),
            'interior_color': request.form.get('interior_color', ''),
            'brand': request.form.get('brand', ''),
            'year': get_int_value(request.form.get('year')),
            'daily_rate': get_numeric_value(request.form.get('daily_rate'), 0.0),
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
        # 修改檢查條件
        if 'files' not in request.files or 'carId' not in request.form:
            flash('請選擇檔案並提供車輛 ID')
            return redirect(request.url)

        files = request.files.getlist('files')  # 取得多個檔案
        car_id = request.form.get('carId')
        folder_name = request.form.get('folderName')

        # 檢查是否有選擇檔案
        if not files or all(file.filename == '' for file in files):
            flash('請選擇至少一個檔案')
            return redirect(request.url)

        if not car_id.isdigit():
            flash('車輛 ID 必須是有效的數字')
            return redirect(request.url)

        car_id = int(car_id)

        # 確保 car_id 存在於 Car 表中
        sql = text("SELECT * FROM cars WHERE id = :car_id")
        result = db.session.execute(sql, {"car_id": car_id})
        car = result.fetchone()
        if not car:
            flash('提供的車輛 ID 無效，請選擇有效的車輛')
            return redirect(request.url)

        s3_service = S3Service()
        successful_uploads = 0
        failed_uploads = 0

        # 迴圈處理每個檔案
        for file in files:
            if file.filename == '':
                continue

            if not s3_service.allowed_file(file.filename):
                flash(f'檔案 {file.filename} 格式不支援，只允許上傳圖片格式 (png, jpg, jpeg, gif)')
                failed_uploads += 1
                continue

            # 上傳到 S3
            file_url = s3_service.upload_file(file, file.filename, folder_name)

            if file_url:
                # 儲存到資料庫
                new_image = CarImages(
                    car_id=car.id,
                    image_url=file_url,
                    created_by_id=current_user.id
                )
                db.session.add(new_image)
                successful_uploads += 1
            else:
                flash(f'檔案 {file.filename} 上傳失敗')
                failed_uploads += 1

        # 批次提交到資料庫
        try:
            db.session.commit()
            if successful_uploads > 0:
                flash(f'成功上傳 {successful_uploads} 張圖片到車輛 ID: {car.id}')
            if failed_uploads > 0:
                flash(f'{failed_uploads} 張圖片上傳失敗')
        except Exception as e:
            db.session.rollback()
            flash('資料庫儲存失敗，請重試')

        return redirect(url_for('controller.admin_upload'))

    # GET 請求的處理保持不變
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