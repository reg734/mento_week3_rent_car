import boto3
from flask import current_app

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_S3_REGION']
        )
        self.bucket_name = current_app.config['AWS_S3_BUCKET_NAME']

    def upload_file(self, file, filename):
        try:
            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                filename
            )
            file_url = f"https://{self.bucket_name}.s3.{current_app.config['AWS_S3_REGION']}.amazonaws.com/{filename}"
            return file_url
        except Exception as e:
            print(f"Error uploading file to S3: {e}")
            return None
    
    # 定義允許的圖片擴展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(self, filename):
        """檢查檔案是否符合允許的擴展名"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS