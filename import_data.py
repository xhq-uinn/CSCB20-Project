# In this file we:
# import fake items from external csv
# conduct data cleaning

import pandas as pd
import random
import math
import ast
import json
from datetime import datetime, timedelta
import os
import sqlite3




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
    "description"
]
df = df.drop(columns=columns_to_drop, errors="ignore")


# change category tree to the first category in the tree
# and delete niche category (item # <=2)
def get_main_category(category_str):
    if pd.isna(category_str):
        return None

    try:
        category_list = ast.literal_eval(category_str)

        if isinstance(category_list, list) and len(category_list) > 0:
            first_path = category_list[0]

            if isinstance(first_path, str) and first_path.strip():
                main_category = first_path.split(">>")[0].strip()
                return main_category

        return None
    except:
        return None
    
df["category"] = df["product_category_tree"].apply(get_main_category)

category_counts = df["category"].value_counts()
valid_categories = category_counts[category_counts >= 3].index
df = df[df["category"].isin(valid_categories)]


#change "retail_price" to numeric type
df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce")

#original "retail_price" too large, so divided by 100 and take ceiling function
df["price"] = df["retail_price"].apply(
    lambda x: math.ceil(x / 100) if pd.notna(x) else None
)

#original item images is a list, we take first valid image from it
def get_first_valid_image(image_str):
    if pd.isna(image_str): #if list empty
        return ""

    try:
        image_list = ast.literal_eval(image_str)

        if isinstance(image_list, list):
            for img in image_list:
                if isinstance(img, str) and img.strip():
                    return img.strip()

        return ""
    except Exception as e:
        print("JSON ERROR:", e)
        return ""

df["image_url"] = df["image"].apply(get_first_valid_image)


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

def random_datetime(start, end):
    delta_seconds = int((end - start).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    return start + timedelta(seconds=random_seconds)

df["update_timestamp"] = [
    random_datetime(start_time, end_time).strftime("%Y-%m-%d %H:%M:%S")
    for _ in range(len(df))
]


# add new column: likes(initial value 0)
df["likes"] = 0


# deal with empty value
df["product_name"] = df["product_name"].fillna("Unknown Product")
df["product_specifications"] = df["product_specifications"].fillna("")
df["product_category_tree"] = df["product_category_tree"].fillna("Unknown Category")


init_db()

conn = sqlite3.connect("items.db")


insert_sql = (
    "INSERT INTO items (name, category, price, image, product_specification, condition, update_timestamp, likes) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)

params = [
    (
        row["product_name"],
        row["category"],
        row["price"],
        row["image_url"],
        row["product_specifications"],
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


