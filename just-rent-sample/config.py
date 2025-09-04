import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    POSTS_PER_PAGE = 7
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION')

    # TapPay 配置
    TAPPAY_APP_ID = os.environ.get('TAPPAY_APP_ID')
    TAPPAY_APP_KEY = os.environ.get('TAPPAY_APP_KEY')
    TAPPAY_SANDBOX = os.environ.get('TAPPAY_SANDBOX', 'true').lower() == 'true'
    TAPPAY_MERCHANT_ID = os.environ.get('TAPPAY_MERCHANT_ID', '')
