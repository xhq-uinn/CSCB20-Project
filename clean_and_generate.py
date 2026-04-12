import re
import sqlite3
import requests
from tqdm import tqdm

DB_PATH = "items.db"


# 1️⃣ 解析 spec（核心）
def parse_spec(s):
    if not s:
        return {}

    pairs = re.findall(r'"key"=>"(.*?)",\s*"value"=>"(.*?)"', s)
    return dict(pairs)


# 2️⃣ 清洗（通用，不依赖 key）
def clean_spec(data):
    cleaned = {}

    for k, v in data.items():
        k = k.strip()
        v = v.strip()

        if not v:
            continue

        # Yes/No → bool
        if v.lower() == "yes":
            v = True
        elif v.lower() == "no":
            v = False

        cleaned[k] = v

    return cleaned


# 3️⃣ 调用本地 gemma
def gen_desc(spec):
    prompt = f"""
Convert the following product specifications into a short ecommerce description.

Rules:
- Keep it under 30 words
- Do not invent missing info
- Use natural English

Specs:
{spec}
"""

    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        return r.json()["response"].strip()

    except Exception as e:
        return f"[ERROR] {e}"


# 4️⃣ 主流程（批量处理）
def process_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 确保字段存在
    cursor.execute("""
    ALTER TABLE items ADD COLUMN spec_clean TEXT
    """)
    cursor.execute("""
    ALTER TABLE items ADD COLUMN spec_text TEXT
    """)
    conn.commit()

    # 读取数据
    cursor.execute("SELECT id, product_specification FROM items")
    rows = cursor.fetchall()

    print(f"Total items: {len(rows)}")

    for item_id, raw_spec in tqdm(rows):
        parsed = parse_spec(raw_spec)
        cleaned = clean_spec(parsed)

        # 转字符串存
        clean_str = str(cleaned)

        # 生成描述
        text = gen_desc(cleaned)

        # 写回
        cursor.execute("""
            UPDATE items
            SET spec_clean = ?, spec_text = ?
            WHERE id = ?
        """, (clean_str, text, item_id))

        conn.commit()

    conn.close()


if __name__ == "__main__":
    process_all()