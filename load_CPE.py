import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, os, re
import pandas as pd

# 市價對象的解析函數
def valid_price(price):
    # 檢查價格是否為有效格式
    if not re.match(r"^\$\d{1,3}(,\d{3})*(\.\d{1,2})?$", price):
        return None
    price = price.replace("$", "")
    price = price.replace(",", "")
    return float(price)

# 保存數據到JSON文件
def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# 從JSON文件加載數據
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    else:
        return {}

# 主程序
def main():
    excel_file = '1120612_CPE.xlsx'
    json_file = 'data.json'

    # 檢查是否存在已處理的數據文件
    if json_file in os.listdir():
        data = load_data(json_file)
    else:
        data = {}

    # 讀取 Excel 數據
    df = pd.read_excel(excel_file, skiprows=2)

    # 遍歷每一行的數據
    for i, row in df.iterrows():
        category = row['類別']
        company = row['廠商']
        brand = row['#品牌']
        product_name = row['#產品名稱']
        model = row['#型號']
        price = row['寬頻優惠價\n(以系統價格為準)']

        print(f'正在處理 {product_name} ({i+1}/{len(df)})...')

        # 檢查是否已處理過該行數據
        if str(i) in data:
            # 已處理過，跳過當前行
            print(f'跳過 {product_name} (已處理)')
            continue

        # 設置Chrome瀏覽器選項
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 無頭模式，不顯示瀏覽器界面
        browser = webdriver.Chrome(options=chrome_options)

        # 搜索Google市價
        search_url = f'https://www.google.com/search?q={product_name}'
        sleep_times = 3
        for j in range(3):
            browser.get(search_url)
            time.sleep(sleep_times)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            market_product = soup.find_all('div', {'class': 'rwVHAc itPOE'})
            if market_product:
                break
            if j < 3:
                print(f'重試 {product_name}... (重試次數: {j + 1}/{3})')
                sleep_times += 1
        # 儲存市價數據
        prices = []
        for j, product in enumerate(market_product):
            price_tag = product.find('div', {'class': 'T4OwTb'})
            if price_tag:
                market_price = valid_price(price_tag.text)
                if market_price is not None:
                    shop_tag = product.find('div', {'class': 'LbUacb'})
                    shop_name = shop_tag.text if shop_tag else ''

                    shop_url_tag = product.find('a', {'class': 'plantl pla-unit-title-link'})
                    shop_url = shop_url_tag['href'] if shop_url_tag else ''
                    prices.append((market_price, shop_name, shop_url))

        # 計算最小值、最大值和中位數
        min_price = min(prices, key=lambda x: x[0])[0] if prices else None
        max_price = max(prices, key=lambda x: x[0])[0] if prices else None
        median_price = sorted(prices, key=lambda x: x[0])[len(prices) // 2][0] if prices else None
        is_cheaper = float(price) < float(median_price) if price and median_price else None

        # 保存數據
        data[str(i)] = {
            'category': category,
            'company': company,
            'brand': brand,
            'product_name': product_name,
            'model': model,
            'price': price,
            'prices': prices,
            'min_price': min_price,
            'max_price': max_price,
            'median_price': median_price,
            'is_cheaper': is_cheaper
        }

        # 保存已處理完成的數據
        save_data(data, json_file)
        browser.quit()
        print(f'{product_name} (處理完成)')

    print('數據處理完成。')

if __name__ == '__main__':
    main()
