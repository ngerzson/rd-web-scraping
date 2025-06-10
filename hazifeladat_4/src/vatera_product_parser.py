import os
import json
import re
from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---- Alap beállítások ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_vatera.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_vatera_enriched.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---- Termék specifikációk kinyerése ----
def extract_specs(soup):
    specs = {}

    rows = soup.select("div.tw-grid.tw-gap-2.tw-grid-cols-[auto_1fr]")
    for row in rows:
        cols = row.find_all("div", recursive=False)
        if len(cols) != 2:
            continue
        label = cols[0].get_text(strip=True)
        value = cols[1].get_text(strip=True)

        if label == "Memória gyártó:":
            specs["brand"] = value
        elif label == "Processzor típusa:":
            specs["cpu"] = value
        elif label == "Tárolókapacitás:":
            specs["storage"] = value

    return specs

# ---- Leírás kinyerése ----
def extract_description(soup):
    desc_block = soup.select_one("div.tw-break-words.tw-flex.tw-flex-col.tw-gap-3")
    if desc_block:
        text = desc_block.get_text(separator="\n", strip=True)
        return re.sub(r"\n+", "\n", text)
    return ""

# ---- Parser fő futtatása ----
def run_parser():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    enriched = []

    for product in tqdm(products, desc="🔍 Vatera termékoldalak feldolgozása"):
        url = product.get("product_link")
        if not url:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            specs = extract_specs(soup)
            description = extract_description(soup)

            # Mezők hozzáadása a termékhez
            product["brand"] = specs.get("brand")
            product["cpu"] = specs.get("cpu")
            product["storage"] = specs.get("storage")
            product["description"] = description

            enriched.append(product)

        except Exception as e:
            tqdm.write(f"⚠️ Hiba: {url} → {e}")
            continue

        # sleep(1.5)  # kímélő mód

    # Mentés JSON fájlba
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Bővített adatok elmentve ide: {OUTPUT_FILE}")

# ---- Főprogram hívása ----
if __name__ == "__main__":
    run_parser()