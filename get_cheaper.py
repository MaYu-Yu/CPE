import json
import os
from urllib.parse import quote
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import uuid

data_file = 'data.json'
cheaper_file = 'cheaper.json'
img_folder = 'static/img/'

with open(data_file, 'r') as f:
    data = json.load(f)

processed_data = {}
if os.path.exists(cheaper_file):
    with open(cheaper_file, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)

if not os.path.exists(img_folder):
    os.makedirs(img_folder)

last_index = max([int(index) for index in processed_data.keys()], default=-1)

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
max_data_len = len(data)
for i, (index, product) in enumerate(data.items()):
    index = str(int(index))
    if index in processed_data:
        continue
    print(f'開始處理產品({index}/{max_data_len})..')
    retry_count = 0
    while retry_count < 3:
        try:
            product_name = product['product_name']
            img_path = ''
            unique_filename = str(uuid.uuid4())
            if os.path.exists(img_folder + unique_filename + '.jpg'):
                img_path = img_folder + unique_filename + '.jpg'
            else:
                query = quote(product_name)
                url = f'https://www.google.com/search?q={query}&source=lnms&tbm=isch&sa=X'
                driver.get(url)
                time.sleep(3)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                img_div = soup.find_all('img', {'class': 'rg_i Q4LuWd'})
                if img_div:
                    img_data = img_div[0]['src']
                    img_data = img_data.split(',')[1]
                    img_data = base64.b64decode(img_data)
                    img_path = f'{img_folder}{unique_filename}.jpg'
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    img_path = f'{unique_filename}.jpg'
                else:
                    img_path = None
            product['img_path'] = img_path
            processed_data[index] = product
            with open(cheaper_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=4, ensure_ascii=False)
            break  # 成功處理圖像
        except Exception as e:
            print(f'Error發生: {str(e)}')
            retry_count += 1
            print(f'重新搜尋當前產品 (Retry count: {retry_count})')

    if retry_count == 3:
        print("搜尋過多次失敗...")
    else:
        print(f'處理完成 ({index})')
print("全部產品處理完成!")
driver.quit()
