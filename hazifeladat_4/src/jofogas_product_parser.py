import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---- Alap beállítások ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas_enriched.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# ---- Szelektorok ----
SELECTORS = {
    "brand": 'div[data-testid="param_laptop_acc_brand"] h6 span',
    "cpu": 'div[data-testid="param_computer_cpu_type"] h6 span',
    "storage": 'div[data-testid="param_capacity"] h6 span',
    "description": 'p.MuiTypography-root.MuiTypography-body1.css-18q1add'
}

# ---- Segédfüggvény ----
def extract_field(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    enriched = []

    for product in tqdm(products, desc="🔍 Requests feldolgozás", unit="termék"):
        url = product.get("product_link")
        if not url:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            product["brand"] = extract_field(soup, SELECTORS["brand"])
            product["cpu"] = extract_field(soup, SELECTORS["cpu"])
            product["storage"] = extract_field(soup, SELECTORS["storage"])
            product["description"] = extract_field(soup, SELECTORS["description"])

            enriched.append(product)

        except Exception as e:
            tqdm.write(f"⚠️ Hiba: {url} → {e}")
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Mentve: {len(enriched)} termék → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()