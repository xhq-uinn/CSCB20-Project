# In this file we:
# import items data (in csv) from flipkart.com
# do data cleaning

import pandas as pd
import random
import math
import ast
import json
from datetime import datetime, timedelta

from app import app, db, Item


#read original csv file
df = pd.read_csv("data/flipkart_com-ecommerce_sample.csv") 

#delete unwanted columns
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


#change category tree to the first category in the tree
#and delete niche category (item # <=2)
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
        image_list = ast.literal_eval(image_str) #turn string to python list

        if isinstance(image_list, list):
            for img in image_list:
                #img is string and not empty after deleting blank
                if isinstance(img, str) and img.strip(): 
                    return img.strip()

        return ""
    except Exception as e:
        print("JSON ERROR:", e)
        item.product_specification = []

df["image_url"] = df["image"].apply(get_first_valid_image)


#add new column: condition(random)
conditions = [
    "Brand New",
    "Like New",
    "Minor Scratches or Stains",
    "Visible Scratches or Stains",
    "Poor Condition"
]
df["condition"] = [random.choice(conditions) for _ in range(len(df))]


#add new column: update_timestamp(random)
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


#add new column: likes(initial value 0)
df["likes"] = 0


#deal with empty value
df["product_name"] = df["product_name"].fillna("Unknown Product")
df["product_specifications"] = df["product_specifications"].fillna("")
df["product_category_tree"] = df["product_category_tree"].fillna("Unknown Category")



with app.app_context():
    db.session.query(Item).delete()
    db.session.commit()

    items = []

    for _, row in df.iterrows():
        item = Item(
            name=row["product_name"],
            category=row["category"],
            price=row["price"],
            image=row["image_url"],
            product_specification =row["product_specifications"],
            condition=row["condition"],
            update_timestamp=row["update_timestamp"],
            likes=row["likes"]
        )
        items.append(item)

    db.session.bulk_save_objects(items)
    db.session.commit()

    print("Imported rows:", Item.query.count())

print("Data cleaning and import finished.")


