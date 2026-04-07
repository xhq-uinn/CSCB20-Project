from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import json
import sqlite3

app = Flask(__name__)

app.secret_key = "<KEY>"


# index page 
@app.route("/", methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect("instance/items.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM item WHERE category = ? LIMIT 6", ("Pens & Stationery",))
    need_row = cursor.fetchall()

    cursor.execute("SELECT * FROM item WHERE price < 100 AND category != 'clothing' LIMIT 6")
    feature_row = cursor.fetchall()
   
    cursor.close()
    conn.close()

    return render_template("index.html", need_items=need_row, feature_items=feature_row)


# home page
@app.route("/home")
def home():
    conn = sqlite3.connect("instance/items.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM item LIMIT 100")
    items = cursor.fetchall()  

    cursor.close()
    conn.close()

    return render_template("home.html", items=items)


# Category Page
@app.route("/category", methods=["POST"])
def category():
    conn = sqlite3.connect("instance/items.db")
    cursor = conn.cursor()

    category = request.form.get("category")

    query = "SELECT * FROM item WHERE category = ?"
    cursor.execute(query, (category,))
    
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("category.html", category=category, items=items)


# Sell Page
@app.route("/sell")
def sell():
    return render_template("sell.html")


# item detail page
# @app.route("/item//<int:item_id>")  
# def item(item_id):
#     item = Item.query.get(item_id) #query db using item_id
 
#     # change product_specifications collumn to json form
#     if item.product_specification:
#         try:
#             #fix incorrect json
#             fixed = item.product_specification.replace("=>", ":")

#             #change to python dictionary
#             data = json.loads(fixed)

#             #take list
#             item.product_specification = data.get("product_specification", [])

#         except:
#             item.product_specification = []
            
#     return render_template("item.html", items=item) #pass item to html


@app.route("/item", methods=['POST'])
def item():
    conn = sqlite3.connect("instance/items.db")
    cursor = conn.cursor()

    item_id=request.form.get("item_id")

    cursor.execute("SELECT * FROM item WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("item.html", item=item)


# search and filter page
@app.route("/filter")
def filter():
    return render_template("filter.html")

if __name__ == "__main__":
    app.run(debug=True)