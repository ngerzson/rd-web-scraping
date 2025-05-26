import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import os

# 🔗 Kiinduló linkek márkák szerint
brand_urls = {
    "acer": "https://www.vatera.hu/listings/index.php?q=acer+laptop",
    "asus": "https://www.vatera.hu/listings/index.php?q=asus+laptop",
    "lenovo": "https://www.vatera.hu/listings/index.php?q=lenovo+laptop",
    "dell": "https://www.vatera.hu/listings/index.php?q=dell+laptop"
}

# 📋 Szelektor dictionary
selectors = {
    "product_box": "div.gtm-impression.prod",
    "name": "h3",
    "link": "a.product_link",
    "price": "span.originalVal",
    "description": "div.additional-info"
}

headers = {"User-Agent": "Mozilla/5.0"}

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# 🔁 Minden márkára végrehajtjuk a scrapinget
for brand, base_url in brand_urls.items():
    print(f"\n📥 Feldolgozás: {brand.upper()}")
    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Hiba az oldal lekérésekor: {response.status_code}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    page_info_tag = soup.select_one('div[title*="oldal"]')
  
    if page_info_tag:
        title_text = page_info_tag.get("title", "")
        try:
            total_pages = int(title_text.split("/")[1].strip().split()[0])
        except (IndexError, ValueError):
            total_pages = 1
    else:
        total_pages = 1

    print(f"🔢 Oldalak száma: {total_pages}")
    scraped_data = []

    for page_no in range(1, total_pages + 1):
        url = base_url if page_no == 1 else f"{base_url}&p={page_no}"
        print(f"  🌐 Oldal {page_no} lekérése...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"  ⚠️ Hiba az oldalon: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.select(selectors["product_box"])
        print(f"  🔍 Talált termékek: {len(products)}")

        for product in products:
            name_tag = product.select_one(selectors["name"])
            link_tag = product.select_one(selectors["link"])
            price_tag = product.select_one(selectors["price"])
            desc_tag = product.select_one(selectors["description"])
            product_id = product.get("data-product-id", "-")

            if not name_tag or not link_tag or not price_tag:
                continue

            price_numbers = re.findall(r"\d+", price_tag.text)
            price_value = int("".join(price_numbers)) if price_numbers else 0

            description = "-"
            if desc_tag:
                raw_desc = desc_tag.get_text(separator=" | ", strip=True)
                description = clean_text(raw_desc)

            item = {
                "product_link": link_tag.get("href", "-"),
                "category_link": url,
                "page_no": page_no,
                "price": price_value,
                "name": clean_text(name_tag.text),
                "description": description,
                "product_id": product_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            scraped_data.append(item)

    # 📁 JSON mentés
    file_path = f"D:\WebScraping\Tananyag\Házi feladatok\hazifeladat_2_{brand}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Mentve: {file_path} ({len(scraped_data)} termék)")