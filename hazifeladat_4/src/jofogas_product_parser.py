import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm

# Elérési utak
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas_test.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas_enriched.json")

# Szelektorok
SELECTORS = {
    "brand": 'div[data-testid="param_laptop_acc_brand"] span.MuiTypography-subtitle1',
    "cpu": 'div[data-testid="param_computer_cpu_type"] span.MuiTypography-subtitle1',
    "storage": 'div[data-testid="param_capacity"] span.MuiTypography-subtitle1'
}

def extract_field(soup, selector):
    el = soup.select_one(selector)
    return el.text.strip() if el else None

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_product_details(product):
    url = product.get("product_link")
    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Sikertelen lekérés: {url} [{response.status_code}]")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        product["brand"] = extract_field(soup, SELECTORS["brand"])
        product["cpu"] = extract_field(soup, SELECTORS["cpu"])
        product["storage"] = extract_field(soup, SELECTORS["storage"])

        return product

    except Exception as e:
        print(f"⚠️ Hiba a termék feldolgozásakor: {url} → {e}")
        return None

def main():
    print(f"📥 Beolvasás: {INPUT_FILE}")
    products = load_data(INPUT_FILE)
    enriched_data = {}

    print(f"🔍 Termékoldalak feldolgozása ({len(products)} db)...")
    for product in tqdm(products):
        updated = parse_product_details(product)
        if updated:
            enriched_data[updated["product_link"]] = updated

    print(f"\n💾 Mentés: {OUTPUT_FILE}")
    save_data(enriched_data, OUTPUT_FILE)
    print(f"✅ Kész, {len(enriched_data)} termék mentve.")

if __name__ == "__main__":
    main()