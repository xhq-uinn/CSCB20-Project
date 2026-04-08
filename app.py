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
    cursor.execute( #items table
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

    cursor.execute( # users table
        """
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT
            email TEXT UNIQUE,
            password TEXT
        )
        """
    )
    cursor.execute( # likes table
        """
        CREATE TABLE IF NOT EXISTS likes (
            uid INTEGER,
            iid INTEGER,
            PRIMARY KEY (uid, iid),
            FOREIGN KEY (uid) REFERENCES users(uid),
            FOREIGN KEY (iid) REFERENCES items(id)
        )
        """
    )
    cursor.execute( #orders table
        """
        CREATE TABLE IF NOT EXISTS orders (
            oid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER,
            iid INTEGER,
            timestamp TEXT,
            FOREIGN KEY (uid) REFERENCES users(uid),
            FOREIGN KEY (iid) REFERENCES items(id)
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


# Category Page
@app.route("/category", methods=["POST"])
def category():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    category = request.form.get("category")

    cursor.execute("SELECT * FROM items WHERE category = ?", (category,))
    
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
    sequence = request.args.get("sequence")

    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if keyword:
        query += " AND name LIKE ?"
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
    
    if sequence == "PriceL2H":
        query += " ORDER BY price ASC"
    
    if sequence == "PriceH2L":
        query += " ORDER BY price DESC"
        
    if sequence == "LikesH2L":
        query += " ORDER BY likes ASC"

    if sequence == "MostRecent":
        query += " ORDER BY update_timestamp DESC"


    # execute query
    items = cursor.execute(query, params).fetchall()
    
    if not items:  # fetchall() return [], items will never be None
        return("No items found")
    
    conn.close()

    #return filtered items to html
    return render_template("filter.html", items=items)


@app.route("/signup", method=["GET", "POST"])
def signup():
    email = request.form.get("username")
    password = request.form.get("password")
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.exec("") #sql怎么写
    cursor.commit()
    conn.close()

@app.route("login", method=["GET", "POST"])
def login():
    email = request.form.get("username")
    password = request.form.get("password")


if __name__ == "__main__":
    app.run()