import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_static_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 廠牌
    brand = soup.select_one(".bread a[href*='/make/']")
    brand_name = brand.text.strip() if brand else "無資料"

    # 車款標題
    title = soup.select_one(".trim-main h1.title")
    car_title = title.text.strip() if title else "無資料"

    # 主圖（第一張）
    img = soup.select_one(".trim-carousel img")
    img_url = img.get("src") if img else "無圖片"

    return {
        "廠牌": brand_name,
        "車款": car_title,
        "圖片": img_url,
    }


def get_dynamic_spec(url):
    options = Options()
    options.add_argument('--headless')  # 背景執行
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 15)

    # 點擊「規格配備」tab
    try:
        tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tab-id='spec']")))
        tab.click()
        time.sleep(3)
    except Exception as e:
        print("⚠️ 無法點擊規格配備頁籤：", e)

    # 等待 spec 區塊載入
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".trim-spec-detail .spec-wrapper")))
        time.sleep(1)
    except Exception as e:
        print("⚠️ 規格未及時出現，嘗試備援等待")
        time.sleep(5)

    # 抓資料
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    spec_data = {}

    for li in soup.select(".trim-spec-detail .spec-wrapper li"):
        spans = li.select("span")
        if len(spans) >= 2:
            key = spans[0].text.strip()
            val = spans[1].text.strip()
            spec_data[key] = val

    driver.quit()
    return spec_data


def yahoo_combined_crawler(url):
    static = get_static_data(url)
    dynamic = get_dynamic_spec(url)

    # 合併資料
    car_info = {
        **static,
        "排氣量": dynamic.get("排氣量", "無資料"),
        "車身型式": dynamic.get("車身型式", "無資料"),
        "車門數": dynamic.get("車門數", "無資料"),
        "座位數": dynamic.get("座位數", "無資料"),
        "車長": dynamic.get("車長", "無資料"),
        "軸距": dynamic.get("軸距", "無資料"),
        "引擎型式": dynamic.get("引擎型式", "無資料"),
        "動力型式": dynamic.get("動力型式", dynamic.get("驅動型式", "無資料")),
    }

    for k, v in car_info.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    yahoo_combined_crawler("https://autos.yahoo.com.tw/new-cars/trim/suzuki-swift-2016-1-.-2-glx/spec")
