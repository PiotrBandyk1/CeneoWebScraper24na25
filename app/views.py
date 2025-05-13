import os
import json
from datetime import datetime
from app import app
from flask import render_template, redirect, url_for, request, send_from_directory

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/extract', methods=['POST'])
def extract_data():
    product_id = request.form.get('product_id')
    return redirect(url_for('product', product_id=product_id))

@app.route('/extract', methods=['GET'])
def display_form():
    return render_template("extract.html")

@app.route('/products')
def products():
    products = []
    try:
        print("Pliki w folderze ./app/data/products:", os.listdir("./app/data/products"))

        for file in os.listdir("./app/data/products"):
            if file.endswith(".json"):
                with open(os.path.join("./app/data/products", file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    products.append(data)
                    print(f"Załadowano produkt: {data.get('product_name')}")
        
        if not products:
            print("Brak produktów w katalogu!")
        
    except Exception as e:
        print(f"Napotenano błąd: {e}")
    
    return render_template("products.html", products=products)

@app.route('/author')
def author():
    return render_template("author.html")

def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None
    return None

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    product_path = os.path.join("./app/data/products", f"{product_id}.json")

    print(f"Ścieżka produktu: {product_path}")
    
    if not os.path.exists(product_path):
        return f"Produkt o ID {product_id} nie istnieje.", 404
    
    with open(product_path, "r", encoding="utf-8") as f:
        product_data = json.load(f)
    
    opinions_path = os.path.join("./app/data/opinions", f"{product_id}.json")

    if os.path.exists(opinions_path):
        with open(opinions_path, "r", encoding="utf-8") as f:
            opinions_data = json.load(f)
    else:
        opinions_data = []

    sort_by = request.args.get('sort_by', 'opinion_id')
    reverse = request.args.get('reverse', 'false') == 'true'

    if sort_by == 'purchase_date':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: parse_date(x.get('purchase_date')) if parse_date(x.get('purchase_date')) else datetime.min,
            reverse=reverse
        )
    elif sort_by == 'pros':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: len(x.get('pros', [])),
            reverse=reverse
        )
    elif sort_by == 'cons':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: len(x.get('cons', [])),
            reverse=reverse
        )
    else:
        opinions_data = sorted(opinions_data, key=lambda x: x.get(sort_by), reverse=reverse)

    filter_by = request.args.get('filter_by', '').strip().lower()
    if filter_by:
        opinions_data = [
            op for op in opinions_data if any(
                filter_by in str(op.get(key, '')).lower() for key in ['opinion_id', 'content', 'author', 'recommendation', 'stars', 'pros', 'cons']
            )
        ]

    return render_template("product.html", product=product_data, opinions=opinions_data)

@app.route('/download_json/<product_id>')
def download_json(product_id):
    opinions_directory = os.path.abspath("./app/data/opinions")
    opinion_file_name = f"{product_id}.json"
    opinion_file_path = os.path.join(opinions_directory, opinion_file_name)

    if not os.path.exists(opinion_file_path):
        return f"Plik z opiniami dla produktu {product_id} nie istnieje.", 404
    return send_from_directory(directory=opinions_directory, path=opinion_file_name, as_attachment=True)

@app.route('/charts/<product_id>')
def charts(product_id):
    product_path = os.path.join("./app/data/products", f"{product_id}.json")

    print(f"Ścieżka produktu: {product_path}")
    
    if not os.path.exists(product_path):
        return f"Produkt o ID {product_id} nie istnieje.", 404
    
    with open(product_path, "r", encoding="utf-8") as f:
        product_data = json.load(f)
    return render_template("charts.html", product=product_data)
