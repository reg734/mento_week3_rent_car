import requests
from bs4 import BeautifulSoup
def yahoo_car_crawler():
    url = "https://autos.yahoo.com.tw/new-cars/trim/suzuki-swift-2016-1-.-2-glx"  # 將網址存入變數
    response = requests.get(url)  # 發送 GET 請求
    soup = BeautifulSoup(response.text, "html.parser")  # 解析 HTML

    # 使用 CSS 選擇器來選取元素
    car_info = {
        "排氣量": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "車身型式": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "座位數": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "車門數": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "車長": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "軸距": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "動力型式": soup.select_one(".spec-wrapper li span:nth-child(2)").text,
        "廠牌": soup.select_one('a[title="Suzuki"]').text,
        "車款": soup.select_one(".trim-main h1.title").text
    }

    print(car_info)
