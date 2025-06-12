import os
import time
import json
import re
from datetime import datetime
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Dátum és fájl útvonalak ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{TODAY}_jofogas.json")
PROFILE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "chrome_profile"))

BASE_URL = "https://www.jofogas.hu/magyarorszag/laptop-es-kiegeszitok"

# ---- Selenium driver beállítása ----
def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
    }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

# ---- Termékek kigyűjtése egy oldalról ----
def extract_products_from_page(driver):
    product_data = []
    product_boxes = driver.find_elements(By.CSS_SELECTOR, 'div[itemscope][itemprop="item"][itemtype="http://schema.org/Product"]')

    for box in product_boxes:
        try:
            link_el = box.find_element(By.CSS_SELECTOR, 'h3.item-title a')
            link = link_el.get_attribute("href")
            name = link_el.text.strip()

            price_el = box.find_element(By.CSS_SELECTOR, 'div.priceBox span.price-value')
            raw_price = price_el.text.strip()
            price = int(re.sub(r'\D+', '', raw_price))

            image_el = box.find_element(By.CSS_SELECTOR, 'section.imageBox img')
            image = image_el.get_attribute("src")

            product_data.append({
                "product_link": link,
                "image": image,
                "name": name,
                "price": price,
                "category_link": driver.current_url,
                "source": "jofogas",
                "date": TODAY
            })

        except Exception as e:
            tqdm.write(f"⚠️ Hiba terméknél: {e}")
            continue

    return product_data

# ---- Fő scraper logika ----
def run_scraper():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    driver = setup_driver()
    driver.get(BASE_URL)

    try:
        consent_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".didomi-continue-without-agreeing"))
        )
        consent_btn.click()
    except:
        tqdm.write("ℹ️ Consent gomb már el lett fogadva vagy nem jelent meg.")

    all_data = []
    page = 1
    with tqdm(desc="🔄 Oldalak bejárása", unit="oldal") as pbar:
        while True:
            pbar.set_postfix(oldal=page)
            time.sleep(2)
            all_data.extend(extract_products_from_page(driver))

            try:
                current_url = driver.current_url
                next_button = driver.find_element(By.CSS_SELECTOR, ".ad-list-pager-item-next")
                if next_button.is_enabled():
                    next_button.click()
                    WebDriverWait(driver, 5).until(EC.url_changes(current_url))
                    page += 1
                    pbar.update(1)
                else:
                    tqdm.write("✅ Nincs további oldal (Tovább gomb disabled).")
                    break
            except:
                tqdm.write("⛔ Lapozó gomb nem található. Vége.")
                break

    driver.quit()

    # 💾 Mentés
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Összesen {len(all_data)} termék mentve → {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()