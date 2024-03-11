import requests
from bs4 import BeautifulSoup

def sscar_crawler(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-small')
    result = []
    for product in products:
        name = product.find('a', class_='woocommerce-LoopProduct-link').text
        url = product.find('a', class_='woocommerce-LoopProduct-link')['href']
        result.append({'name': name, 'url': url})
    return result

# 使用範例
url = "https://sscars.com.tw/car/"
cars_list = sscar_crawler(url)
print(cars_list)


