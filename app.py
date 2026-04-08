from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import json
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = "yes-this-is-a-secret"

# initialize: items(id(PK), name, category, price, image,
# product_specification, condition, update_timestamp, likes)
def init_db():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price INTEGER,
            image TEXT,
            product_specification TEXT,
            condition TEXT,
            update_timestamp TEXT,
            likes INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

# @app.before_first_request
# def load_data():
#     import import_data


# home page
# take 20 items, pass them to HTML
@app.route("/")
def home():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    items_20 = cursor.execute("SELECT * FROM items LIMIT 20").fetchall()
    conn.close()
    return render_template("home.html", items=items_20)

@app.route("/")
def big_search_bar():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    keyword = request.form.get("keyword")
    cursor.execute("SELECT * FROM item WHERE name = ?", (keyword,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("filter.html", items = items)



# Category Page
@app.route("/category", methods=["POST"])
def category():
    conn = sqlite3.connect("instance/items.db")
    cursor = conn.cursor()

    category = request.form.get("category")

    cursor.execute("SELECT * FROM item WHERE category = ?", (category,))
    
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("category.html", category=category, items=items)


# Sell Page
@app.route("/sell")
def sell():
    return render_template("sell.html")


# item detail page
@app.route("/item/<int:item_id>")
def item(item_id):
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    item =cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    # 怎么处理item DNE？还没写完
    if item is None:
        return "Item not found"

    return render_template("item.html", item=item)


# search and filter page
@app.route("/filter", methods=["GET", "POST"])
def filter_page():
    # get the user filter arguments
    category = request.args.get("category")
    keyword = request.args.get("keyword")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    conditions = request.args.getlist("condition")

    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)

    if keyword:
        query += " AND LOWER(name) LIKE LOWER(?)"
        params.append(f"%{keyword}%")

    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    if min_price:
        query += " AND price >= ?"
        params.append(min_price)

    if conditions:
        query += " AND condition IN ({})".format(",".join(["?"] * len(conditions)))
        params.extend(conditions)

    # execute query
    items = cursor.execute(query, params).fetchall()

    conn.close()

    #return filtered items to html
    return render_template("filter.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)