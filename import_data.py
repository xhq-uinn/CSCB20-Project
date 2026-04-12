# In this file we:
# import fake items from external csv
# conduct data cleaning

# print("START")
import pandas as pd
import random
import math
import ast
import json
import re
from datetime import datetime, timedelta
import os
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
valid_categories = category_counts[category_counts >= 100].index
df = df[df["category"].isin(valid_categories)]


#change "retail_price" to numeric type
df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce")

#original "retail_price" too large, so divided by 100 and take ceiling function
df["price"] = df["retail_price"].apply(
    lambda x: math.ceil(x / 100) if pd.notna(x) else None    
)
df["price"] = df["retail_price"].apply(
    lambda x: math.ceil(x / 100) if pd.notna(x) else 1
).astype(int)

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

def is_basic_valid_image_url(url):
    if pd.isna(url) or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    return url.startswith("http://") or url.startswith("https://")

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
    except:
        return False
    
df = df[df["image_url"].apply(is_reachable_image_url)]




def clean_product_specification(raw):
    if pd.isna(raw) or not isinstance(raw, str) or not raw.strip():
        return ""

    try:
        pairs = re.findall(r'"key"=>"(.*?)",\s*"value"=>"(.*?)"', raw, flags=re.DOTALL)

        cleaned_pairs = []
        seen_keys = set()

        for k, v in pairs:
            k = re.sub(r"\s+", " ", k).strip()
            v = re.sub(r"\s+", " ", v).strip()

            if not k or not v:
                continue

            # 同一个 key 只保留第一次
            if k in seen_keys:
                continue

            seen_keys.add(k)
            cleaned_pairs.append(f"{k}: {v}")

        return "\n".join(cleaned_pairs)

    except Exception as e:
        print("SPEC CLEAN ERROR:", e)
        return ""
    
df["spec_clean"] = df["product_specifications"].apply(clean_product_specification)

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


