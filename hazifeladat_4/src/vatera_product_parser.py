import os
import json
import re
from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---- Beállítások ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_vatera.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_vatera_enriched.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---- Specifikációk kinyerése ----
def extract_specs(soup):
    specs = {"brand": "", "cpu": "", "storage": ""}

    # minden címke mező (label)
    for lbl in soup.select("div.tw-text-warm-grey-600"):
        key = lbl.get_text(strip=True).rstrip(":")
        val_div = lbl.find_next_sibling("div")
        val = val_div.get_text(strip=True) if val_div else ""

        if key == "Memória gyártó":
            specs["brand"] = val
        elif key == "Processzor típusa":
            specs["cpu"] = val
        elif key == "Tárolókapacitás":
            specs["storage"] = val

    return specs

# ---- Leírás kinyerése ----
def extract_description(soup):
    desc_block = soup.select_one("div.tw-break-words.tw-flex.tw-flex-col.tw-gap-3")
    if desc_block:
        text = desc_block.get_text(separator="\n", strip=True)
        return re.sub(r"\n+", "\n", text)
    return ""

# ---- Parser futtatása ----
def run_parser():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    enriched = []

    for product in tqdm(products, desc="🔎 Vatera termékek feldolgozása", unit="db"):
        url = product.get("product_link")
        if not url:
            continue

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            specs = extract_specs(soup)
            description = extract_description(soup)

            product["brand"]      = specs.get("brand", "")
            product["cpu"]        = specs.get("cpu", "")
            product["storage"]    = specs.get("storage", "")
            product["description"]= description or ""

            enriched.append(product)

        except Exception as e:
            tqdm.write(f"⚠️ Hiba a lekérésnél: {url} → {e}")
            continue

        sleep(1.0)

    # Mentés JSON-be
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Feldolgozva: {len(enriched)} termék. Eredmény: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_parser()