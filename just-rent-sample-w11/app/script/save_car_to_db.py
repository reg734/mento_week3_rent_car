# save car_list to db
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Car
from config import Config

# 建立資料庫連線
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)

# 建立 Session 類別
Session = sessionmaker(bind=engine)

# 建立 Session 物件
session = Session()

# 取得目前檔案所在目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "../script/car.json")
#可以讓路徑在不同平台（如 Windows, macOS, Linux）下運作得更穩定與一致。
json_path = os.path.normpath(json_path)
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)




# 將 JSON 數據轉換為 Car 物件並添加到 session
for item in data:
    car = Car(
        name=item['name'],
        seat_number=item['seat'],
        door_number=item['door'],
        body=item['body'],
        displacement=item['displacement'],
        car_length=item['car_length'],
        wheelbase=item['wheelbase'],
        power_type=item['power_type'],
        brand=item['brand'],
        model=item['model'],
    )
    session.add(car)

# 提交 session
session.commit()

# 關閉 session
session.close()
