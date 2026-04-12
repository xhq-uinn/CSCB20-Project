import pandas as pd
import random
import math
import ast
from datetime import datetime, timedelta
import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor

# ================= DB =================
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


# ================= DATA CLEAN =================
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
    except:
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
    except:
        return ""


# ================= 🚀 FAST IMAGE CHECK =================
session = requests.Session()

def is_reachable_image_url_fast(url, timeout=3):
    if not isinstance(url, str):
        return False

    url = url.strip()
    if not url.startswith("http"):
        return False

    try:
        r = session.head(url, timeout=timeout, allow_redirects=True)

        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "").lower()
            return "image" in content_type or content_type == ""

        if r.status_code in (403, 405):
            r = session.get(url, timeout=timeout, stream=True)
            if r.status_code == 200:
                content_type = r.headers.get("Content-Type", "").lower()
                return "image" in content_type

        return False
    except:
        return False


def filter_images_parallel(urls, max_workers=30):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(is_reachable_image_url_fast, urls))
    return results


# ================= RANDOM DATA =================
def random_datetime(start, end):
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))


# ================= MAIN =================

# 1️⃣ 读取数据
df = pd.read_csv("data/flipkart_com-ecommerce_sample.csv")

# 2️⃣ 删除不需要列
columns_to_drop = [
    "uniq_id", "crawl_timestamp", "product_url", "pid",
    "discounted_price", "is_FK_Advantage_product",
    "product_rating", "overall_rating", "brand", "description",
]
df = df.drop(columns=columns_to_drop, errors="ignore")

# 3️⃣ 处理空值
df["product_name"] = df["product_name"].fillna("Unknown Product")
df["product_specifications"] = df["product_specifications"].fillna("")
df["product_category_tree"] = df["product_category_tree"].fillna("Unknown Category")

# 4️⃣ 分类处理
df["category"] = df["product_category_tree"].apply(get_main_category)
category_counts = df["category"].value_counts()
valid_categories = category_counts[category_counts >= 100].index
df = df[df["category"].isin(valid_categories)]

# 5️⃣ 价格处理
df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce")
df["price"] = df["retail_price"].apply(
    lambda x: math.ceil(x / 100) if pd.notna(x) else 1
).astype(int)

# 6️⃣ 图片处理
df["image_url"] = df["image"].apply(get_first_valid_image)

# 🚀 ⭐ 限制数据量（很重要）
df = df.head(20000)

# 🚀 ⭐ 快速过滤非法 URL
df = df[df["image_url"].str.startswith("http")]

print("Rows before image filtering:", len(df))

# 🚀 ⭐ 并发检查图片
mask = filter_images_parallel(df["image_url"].tolist(), max_workers=30)
df = df[mask]

print("Rows after image filtering:", len(df))

# 7️⃣ 其他字段
df["spec_clean"] = "This seller did not provide specifications."

conditions = [
    "Brand New", "Like New", "Minor Scratches or Stains",
    "Visible Scratches or Stains", "Poor Condition",
]
df["condition"] = [random.choice(conditions) for _ in range(len(df))]

end_time = datetime(2026, 4, 1, 23, 59, 59)
start_time = end_time - timedelta(days=365)

df["update_timestamp"] = [
    random_datetime(start_time, end_time).strftime("%Y-%m-%d %H:%M:%S")
    for _ in range(len(df))
]

df["likes"] = 0

# ================= DB INSERT =================
init_db()

conn = sqlite3.connect("items.db")

insert_sql = """
INSERT INTO items 
(name, category, price, image, product_specification, condition, update_timestamp, likes) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

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