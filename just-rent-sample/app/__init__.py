from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    # 初始化 LoginManager
    login_manager.init_app(app)

    # 設置未登入時的重定向頁面和提示消息
    login_manager.login_message = '請先登入以訪問此頁面。'

    # 自定義未登入時的重定向邏輯
    @login_manager.unauthorized_handler
    def unauthorized():
        flash(login_manager.login_message, 'warning')
        if request.path.startswith('/admin'):
            return redirect(url_for('controller.admin_login'))
        else:
            return redirect(url_for('controller.login'))

    

    from app.models.users import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  

    from app.controllers import bp as controllers_bp
    app.register_blueprint(controllers_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.models import bp as models_bp
    app.register_blueprint(models_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
