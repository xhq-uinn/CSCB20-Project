# In this file we:
# import fake items from external csv
# conduct data cleaning

import pandas as pd
import random
import math
import ast
from datetime import datetime, timedelta
import sqlite3
import requests


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
            likes INTEGER DEFAULT 0,
            uid INTEGER,
            FOREIGN KEY (uid) REFERENCES users(uid)
        )
        """
    )
    conn.commit()
    conn.close()


def get_main_category(category_str):
    if pd.isna(category_str):
        return None

    try:
        category_list = ast.literal_eval(category_str)

        if isinstance(category_list, list) and len(category_list) > 0:
            first_path = category_list[0]

            if isinstance(first_path, str) and first_path.strip():
                return first_path.split(">>")[0].strip()

        return None
    except Exception:
        return None


def get_first_valid_image(image_str):
    if pd.isna(image_str):
        return ""

    try:
        image_list = ast.literal_eval(image_str)

        if isinstance(image_list, list):
            for img in image_list:
                if isinstance(img, str) and img.strip():
                    return img.strip()

        return ""
    except Exception as e:
        print("IMAGE PARSE ERROR:", e)
        return ""


def is_reachable_image_url(url, timeout=5):
    if pd.isna(url) or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)

        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "").lower()
            return content_type.startswith("image/") or content_type == ""

        if r.status_code in (403, 405):
            r = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
            if r.status_code == 200:
                content_type = r.headers.get("Content-Type", "").lower()
                return content_type.startswith("image/")

        return False
    except Exception:
        return False


def random_datetime(start, end):
    delta_seconds = int((end - start).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    return start + timedelta(seconds=random_seconds)


# read original csv file
df = pd.read_csv("data/flipkart_com-ecommerce_sample.csv")

# delete unwanted columns
columns_to_drop = [
    "uniq_id",
    "crawl_timestamp",
    "product_url",
    "pid",
    "discounted_price",
    "is_FK_Advantage_product",
    "product_rating",
    "overall_rating",
    "brand",
    "description",
]
df = df.drop(columns=columns_to_drop, errors="ignore")

# deal with empty value first
df["product_name"] = df["product_name"].fillna("Unknown Product")
df["product_specifications"] = df["product_specifications"].fillna("")
df["product_category_tree"] = df["product_category_tree"].fillna("Unknown Category")

# change category tree to the first category in the tree
df["category"] = df["product_category_tree"].apply(get_main_category)

category_counts = df["category"].value_counts()
valid_categories = category_counts[category_counts >= 100].index
df = df[df["category"].isin(valid_categories)]

# change retail_price to numeric type
df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce")

# original retail_price too large, so divide by 100 and take ceiling
# if missing, set to 1
df["price"] = df["retail_price"].apply(
    lambda x: math.ceil(x / 100) if pd.notna(x) else 1
).astype(int)

# original item images is a list, we take first valid image from it
df["image_url"] = df["image"].apply(get_first_valid_image)

print("Rows before image filtering:", len(df))
df = df[df["image_url"].apply(is_reachable_image_url)]
print("Rows after image filtering:", len(df))

# set all specifications to fixed text
df["spec_clean"] = "This seller did not provide specifications."

# add new column: condition(random)
conditions = [
    "Brand New",
    "Like New",
    "Minor Scratches or Stains",
    "Visible Scratches or Stains",
    "Poor Condition",
]
df["condition"] = [random.choice(conditions) for _ in range(len(df))]

# add new column: update_timestamp(random)
end_time = datetime(2026, 4, 1, 23, 59, 59)
start_time = end_time - timedelta(days=365)

df["update_timestamp"] = [
    random_datetime(start_time, end_time).strftime("%Y-%m-%d %H:%M:%S")
    for _ in range(len(df))
]

# add new column: likes(initial value 0)
df["likes"] = 0

init_db()

conn = sqlite3.connect("items.db")

insert_sql = (
    "INSERT INTO items "
    "(name, category, price, image, product_specification, condition, update_timestamp, likes) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)

params = [
    (
        row["product_name"],
        row["category"],
        row["price"],
        row["image_url"],
        row["spec_clean"],
        row["condition"],
        row["update_timestamp"],
        row["likes"],
    )
    for _, row in df.iterrows()
]

conn.executemany(insert_sql, params)
conn.commit()

count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
print("Imported rows:", count)

conn.close()