from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = "yes-this-is-a-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///items.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# define entity: Item
# Item(id(PK), name, category, price, image, discription, condition, update_timestamp, likes)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.Text)
    description = db.Column(db.Text)
    condition = db.Column(db.String(100))
    update_timestamp = db.Column(db.String(50))
    likes = db.Column(db.Integer, default=0)
    

with app.app_context():
    db.create_all()

# home page
@app.route("/")
def home():
    items = Item.query.limit(20).all() # take 20 rows from db, save to items
    return render_template("home.html")

# item detail page
@app.route("/item/<int:item_id>")
def item(item_id):
    return render_template("item.html")

# search and filter page
@app.route("/filter")
def filter():
    return render_template("filter.html")

if __name__ == "__main__":
    app.run(debug=True)