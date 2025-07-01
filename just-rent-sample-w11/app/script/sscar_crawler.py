import requests
from bs4 import BeautifulSoup
import json
import os

def sscar_crawler(url, limit=10):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-small')
    result = []
    seen_urls = set()  # 避免重複

    for product in products:
        if len(result) >= limit:
            break  # 已達到上限，停止迴圈

        link_tag = product.find('a', class_='woocommerce-LoopProduct-link')
        if not link_tag:
            continue

        name = link_tag.text.strip()
        car_url = link_tag['href'].strip()

        if car_url in seen_urls:
            continue  # 如果 URL 已處理過，跳過
        seen_urls.add(car_url)

        result.append({'name': name, 'url': car_url})
    return result

def get_yahoo_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find_all('h4')[1].find('a')['href']
        return link
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # return link
# 使用範例
url = "https://sscars.com.tw/car/"
car_list = sscar_crawler(url)
link_list = []

for car in car_list:
    url = car['url']
    if url is not None:
        car['short_link'] = get_yahoo_link(url)

# 將車輛列表轉換為 JSON 格式的字串
car_list_json = json.dumps(car_list)

# 找到目前這支程式所在的資料夾
script_dir = os.path.dirname(os.path.abspath(__file__))

# 建立 JSON 檔案的完整路徑
output_path = os.path.join(script_dir, "car_list.json")

# 儲存 JSON
with open(output_path, "w", encoding="utf-8") as file:
    file.write(car_list_json)


