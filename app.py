from flask import Flask, render_template, request
import json
import re

json_file = 'cheaper.json'

def preprocess_keyword(keyword):
    # 去除前後空格
    keyword = keyword.strip()
    # 處理防呆，防止程式碼崩潰
    keyword = re.sub(r'[^\w\s]', '', keyword)
    return keyword

# Flask
app = Flask(__name__, static_folder='static')
product_list = []  # 儲存產品數據的全局變數

def load_product_data():
    global product_list  # 使用全局變數
    if not product_list:  # 只在第一次請求時讀取 JSON 數據
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            product_list = list(data.values())  # 將產品資料轉換為列表
    return product_list

@app.route('/')
def index():
    product_list = load_product_data()
    return render_template('index.html', products=product_list, keyword='', filters=request.args)  # 將列表和篩選選項傳遞給模板

@app.route('/search')
def search():
    keyword = request.args.get('keyword')  # 获取搜索关键词
    filtered_products = load_product_data()

    if keyword:
        keyword = preprocess_keyword(keyword)  # 预处理关键词
        # 根据勾选的筛选选项进行关键字搜索
        category_checkbox = request.args.get('category_checkbox')
        company_checkbox = request.args.get('company_checkbox')
        brand_checkbox = request.args.get('brand_checkbox')
        product_name_checkbox = request.args.get('product_name_checkbox')
        model_checkbox = request.args.get('model_checkbox')

        if category_checkbox or company_checkbox or brand_checkbox or product_name_checkbox or model_checkbox:
            filtered_products = []
            if category_checkbox:
                filtered_products += [product for product in load_product_data() if keyword in str(product.get('category', ''))]
            if company_checkbox:
                filtered_products += [product for product in load_product_data() if keyword in str(product.get('company', ''))]
            if brand_checkbox:
                filtered_products += [product for product in load_product_data() if keyword in str(product.get('brand', ''))]
            if product_name_checkbox:
                filtered_products += [product for product in load_product_data() if keyword in str(product.get('product_name', ''))]
            if model_checkbox:
                filtered_products += [product for product in load_product_data() if keyword in str(product.get('model', ''))]
        else:
            filtered_products = [product for product in filtered_products if
                                  keyword in str(product.get('product_name', '')) or
                                  keyword in str(product.get('category', '')) or
                                  keyword in str(product.get('company', '')) or
                                  keyword in str(product.get('brand', '')) or
                                  keyword in str(product.get('model', ''))]

    is_cheaper_checkbox = request.args.get('is_cheaper_checkbox')
    if is_cheaper_checkbox:
        filtered_products = [product for product in filtered_products if product.get('is_cheaper')]

    return render_template('index.html', products=filtered_products, keyword=keyword, filters=request.args)

if __name__ == '__main__':
    app.run()
