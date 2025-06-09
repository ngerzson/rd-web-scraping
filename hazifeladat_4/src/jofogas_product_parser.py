import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Fájlok és útvonalak ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_jofogas_enriched.json")
PROFILE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "chrome_profile"))

# ---- Szelektorok (validált) ----
SELECTORS = {
    "brand": 'div[data-testid="param_laptop_acc_brand"] h6 span',
    "cpu": 'div[data-testid="param_computer_cpu_type"] h6 span',
    "storage": 'div[data-testid="param_capacity"] h6 span',
    "description": 'p.MuiTypography-root.MuiTypography-body1.css-18q1add'
}

def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")

    # Gyorsítás: képek, stíluslapok és betűtípusok tiltása
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)

def extract_field(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    driver = setup_driver()
    enriched = []
    cookie_clicked = False  # cookie kezelő csak egyszer

    for product in tqdm(products, desc="📦 Termékek feldolgozása", unit="termék"):
        url = product.get("product_link")
        if not url:
            continue

        try:
            driver.get(url)

            if not cookie_clicked:
                try:
                    consent_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".didomi-continue-without-agreeing"))
                    )
                    consent_btn.click()
                    cookie_clicked = True
                except:
                    pass  # már el lett fogadva vagy nem jelent meg

            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["description"]))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")

            product["brand"] = extract_field(soup, SELECTORS["brand"])
            product["cpu"] = extract_field(soup, SELECTORS["cpu"])
            product["storage"] = extract_field(soup, SELECTORS["storage"])
            product["description"] = extract_field(soup, SELECTORS["description"])

            enriched.append(product)

        except Exception as e:
            tqdm.write(f"⚠️ Hiba: {url} → {e}")

    driver.quit()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Kész: {len(enriched)} termék bővítve → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()