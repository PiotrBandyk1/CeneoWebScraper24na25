from app import app
from flask import render_template, request, redirect, url_for

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        if product_id and product_id.isdigit():
            return redirect(url_for("product", product_id=int(product_id)))
    return render_template("extract.html")

@app.route('/products')
def products():
    return render_template("products.html")

@app.route('/author')
def author():
    return render_template("author.html")

@app.route('/product/<int:product_id>')
def product(product_id: int):
    return render_template("product.html", product_id=product_id)

