from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import json
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = "yes-this-is-a-secret"

# initialize: items(id(PK), name, category, price, image,
# product_specification, condition, update_timestamp, likes, uid)
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
            likes INTEGER DEFAULT 0,
            uid INTEGER,
            FOREIGN KEY (uid) REFERENCES users(uid)
        )
        """
    )

    cursor.execute( # users table
        """
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
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
    # cursor.execute( #orders table
    #     """
    #     CREATE TABLE IF NOT EXISTS orders (
    #         oid INTEGER PRIMARY KEY AUTOINCREMENT,
    #         uid INTEGER,
    #         iid INTEGER,
    #         timestamp TEXT,
    #         FOREIGN KEY (uid) REFERENCES users(uid),
    #         FOREIGN KEY (iid) REFERENCES items(id)
    #     )
    #     """

    # )
    conn.commit()
    conn.close()

init_db()

# @app.before_first_request
# def load_data():
#     import import_data


@app.route("/")
def index():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items ORDER BY update_timestamp DESC LIMIT 6")
    new_items = cursor.fetchall()

    cursor.execute("SELECT * FROM items WHERE likes >= ? LIMIT 6", (1,))
    feature_items = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM items WHERE price > ? AND price < ? AND category = ? LIMIT 6",
        (10, 50, "Pens & Stationery")
    )
    exam_items = cursor.fetchall()

    username = None

    if "uid" in session:
        uid = session["uid"]
        user = cursor.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()

        if user is not None:
            username = user[1]
        else:
            session.clear()

    conn.close()

    return render_template(
        "index.html",
        new_items=new_items,
        feature_items=feature_items,
        exam_items=exam_items,
        username=username
    )

# take 20 items, pass them to HTML
# @app.route("/home")
# def home():
#     conn = sqlite3.connect("items.db")
#     cursor = conn.cursor()
#     items_20 = cursor.execute("SELECT * FROM items LIMIT 100").fetchall()
#     conn.close()

#     if "uid" in session:
#         uid = session["uid"]

#         conn = sqlite3.connect("items.db")
#         cursor = conn.cursor()
        
#         user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
#         username = user[1]

#         conn.close()

#         return render_template("home.html", items=items_20, username=username)
    
#     return render_template("home.html", items=items_20, username=username)


# Category Page
@app.route("/category")
def category():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    category = request.args.get("category")

    cursor.execute("SELECT * FROM items WHERE category = ?", (category,))
    
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if "uid" in session:
        uid = session["uid"]

        conn = sqlite3.connect("items.db")
        cursor = conn.cursor()
        
        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
        username = user[1]

        conn.close()
        return render_template("category.html", category=category, items=items, username=username)

    return render_template("category.html", category=category, items=items)


# item detail page
@app.route("/item")
def item():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    item_id = request.args.get("item_id")
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    # 怎么处理item DNE？还没写完
    if item is None:
        return "Item not found"
    
    if "uid" in session:
        uid = session["uid"]

        cursor.execute("SELECT * FROM users WHERE uid=?", (uid,))
        seller = cursor.fetchone()
        # username = user[1]
        # user=user

        conn.close()

        return render_template("item.html", item=item, seller=seller)
    

    conn.close()
    return render_template("item.html", item=item)


# # like function
@app.route("/like")
def like():
    if "uid" in session:
        uid = session["uid"]
        item_id = request.args.get("item_id")

        conn = sqlite3.connect("items.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()

        cursor.execute("SELECT * FROM likes WHERE uid=? AND iid=?", (uid, item_id))
        existing = cursor.fetchone()

        if existing:
            flash("You already liked this item!")
        else:
            cursor.execute("INSERT INTO likes (uid, iid) VALUES (?, ?)", (uid, item_id))
            cursor.execute("UPDATE items SET likes = likes + 1 WHERE id=?", (item_id,))
            flash("Liked Successfully!")

            conn.commit()

        conn.close()
        
        return redirect(url_for("item", item_id=item_id))
    
    return render_template("login.html")


# filter page
@app.route("/filter")
def filter_page():
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
        query += " AND category LIKE ?"
        params.append(f"%{category}%")

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
        query += " ORDER BY likes DESC"

    if sequence == "MostRecent":
        query += " ORDER BY update_timestamp DESC"


    # execute query
    items = cursor.execute(query, params).fetchall()
    
    # if not items:  # fetchall() return [], items will never be None
    #     return("No items found")
    # HTML里处理items为空
    
    conn.close()

    #return filtered items to html
    return render_template("category.html", category=category, items=items)
    

# search page
@app.route("/search")
def search():
    keyword = request.args.get("keyword")        

    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if keyword:
        query += " AND name LIKE ?"
        params.append(f"%{keyword}%")

    # execute query
    items = cursor.execute(query, params).fetchall()
    
    conn.close()

    if "uid" in session:
        uid = session["uid"]

        conn = sqlite3.connect("items.db")
        cursor = conn.cursor()
        
        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
        username = user[1]

        conn.close()

    #return filtered items to html
    return render_template("search.html", items=items, username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                        (username, email, password)
                        )
            conn.commit()
            conn.close()
        except:
            return("Email already exists")
        

        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("items.db")
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?",
                       (email, password)
                       ).fetchone() # fetchone bc either shown as None or a row
        conn.close()
        if user:
            session["uid"] = user[0]
            return redirect("/")
        else:
            return "Login failed"
        
    return render_template("login.html")


@app.route("/profile")
def profile():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    if "uid" in session:
        uid = session["uid"]

        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

        username = user[1]
        email = user[2]

        item_post = cursor.execute("SELECT * FROM items WHERE uid=? LIMIT 5", (uid,)).fetchall()
        # item_like = cursor.execute("SELECT items.* FROM items JOIN likes ON items.id = likes.iid WHERE likes.uid=? LIMIT 5", (uid,)).fetchall()

        return render_template("profile.html", username=username, email=email, item_post=item_post)

    return render_template("login.html")

# @app.route("/profile_like_all")
# def profile_like__all():
#     conn = sqlite3.connect("items.db")
#     cursor = conn.cursor()

#     if "uid" in session:
#         uid = session["uid"]

#         user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

#         username = user[1]
#         email = user[2]

#         item_post = cursor.execute("SELECT * FROM items WHERE uid=? LIMIT 5", (uid,)).fetchall()
#         item_like = cursor.execute("SELECT items.* FROM items JOIN likes ON items.id = likes.iid WHERE likes.uid=?", (uid,)).fetchall()

#         return render_template("profile-like-all.html", username=username, email=email, item_post=item_post, item_like=item_like)
    
@app.route("/profile_post_all")
def profile_post__all():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    if "uid" in session:
        uid = session["uid"]

        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

        username = user[1]
        email = user[2]

        item_post = cursor.execute("SELECT * FROM items WHERE uid=?", (uid,)).fetchall()
        # item_like = cursor.execute("SELECT items.* FROM items JOIN likes ON items.id = likes.iid WHERE likes.uid=? LIMIT 5", (uid,)).fetchall()

        return render_template("profile-post-all.html", username=username, email=email, item_post=item_post)


@app.route("/like_check")
def like_check_list():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    if "uid" in session:
        uid = session["uid"]

        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

        username = user[1]

        item_like = cursor.execute("SELECT items.* FROM items JOIN likes ON items.id = likes.iid WHERE likes.uid=? LIMIT 5", (uid,)).fetchall()

        return render_template("like.html", username=username, item_like=item_like)

    return render_template("login.html")

@app.route("/like_all")
def like_check_all():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    if "uid" in session:
        uid = session["uid"]

        user = cursor.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

        username = user[1]

        item_like = cursor.execute("SELECT items.* FROM items JOIN likes ON items.id = likes.iid WHERE likes.uid=?", (uid,)).fetchall()

        return render_template("like-all.html", username=username, item_like=item_like)


@app.route("/sell", methods=["GET", "POST"])
def sell():
    if "uid" not in session:
        return redirect("/login")

    uid = session["uid"]

    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        session.clear()
        return redirect("/login")

    if user is None:
        username = None
    else:
        username = user[1]

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        category = request.form.get("category")
        condition = request.form.get("condition")

        file = request.files.get("image")

        image_path = ""
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            os.makedirs("static/uploads", exist_ok=True)
            image_path = os.path.join("static/uploads", filename)
            file.save(image_path)

        cursor.execute(
            """
            INSERT INTO items
            (name, category, price, image, product_specification, condition, update_timestamp, uid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                category,
                int(price) if price else None,
                image_path,
                description,
                condition,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                uid,
            ),
        )

        conn.commit()
        conn.close()
        return redirect("/profile")

    conn.close()
    return render_template("sell.html", username=username)


@app.route("/logout")
def logout():
    session.pop("uid", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)