import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Beállítások ----
BASE_URL = "https://www.jofogas.hu/magyarorszag/laptop-es-kiegeszitok"
TODAY = datetime.now().strftime("%Y_%m_%d")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{TODAY}_jofogas_test.json")
PROFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chrome_profile"))

def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    return webdriver.Chrome(options=options)

def extract_products_from_page(driver):
    product_data = []
    product_boxes = driver.find_elements(By.CSS_SELECTOR, 'div[itemscope][itemprop="item"][itemtype="http://schema.org/Product"]')

    for box in product_boxes:
        try:
            link = box.find_element(By.CSS_SELECTOR, 'section.imageBox a').get_attribute("href")
            image = box.find_element(By.CSS_SELECTOR, 'section.imageBox meta[itemprop="image"]').get_attribute("content")
            name = box.find_element(By.CSS_SELECTOR, 'section.subjectWrapper meta[itemprop="name"]').get_attribute("content")
            price = box.find_element(By.CSS_SELECTOR, 'section.price span.price-value').text.strip()

            product_data.append({
                "product_link": link,
                "image": image,
                "name": name,
                "price": price,
                "category_link": driver.current_url,
                "source": "jofogas",
                "date": TODAY,
            })
        except Exception as e:
            print(f"⚠️ Hiba terméknél: {e}")
            continue

    return product_data

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
        print("ℹ️ Consent gomb nem jelent meg vagy már elfogadva.")

    all_data = []

    for i in range(2):  # Csak két oldal
        print(f"🔄 Oldal {i + 1}")
        time.sleep(2)
        products = extract_products_from_page(driver)
        all_data.extend(products)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".ad-list-pager-item-next")
            if next_button.is_enabled():
                next_button.click()
            else:
                break
        except:
            print("✅ Nincs további oldal.")
            break

    driver.quit()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Mentve: {len(all_data)} termék → {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()
