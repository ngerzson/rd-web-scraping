import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- Beállítások ----
TODAY = datetime.now().strftime("%Y_%m_%d")
BASE_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", f"{TODAY}_vatera.json")

START_URL = "https://www.vatera.hu/szamitastechnika/laptopok-notebook-ok/index-c97.html"
PROFILE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "chrome_profile"))

# ---- Szelektorok ----
SELECTORS = {
    "product_box": 'div.gtm-impression.prod',
    "name": "h3",
    "link": "a.product_link",
    "price": "span.originalVal",
    "image": "img"
}

# ---- Selenium beállítás ----
def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    return webdriver.Chrome(options=options)

# ---- Termékek kinyerése egy oldalról ----
def extract_products_from_page(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_boxes = soup.select(SELECTORS["product_box"])
    items = []

    for i, box in enumerate(product_boxes):
        try:
            # JS-ből betöltött kép külön kérve
            image_elem = driver.find_elements(By.CSS_SELECTOR, SELECTORS["product_box"])[i].find_element(By.CSS_SELECTOR, SELECTORS["image"])
            image = image_elem.get_attribute("data-original") or image_elem.get("src")
            if not image:
                image = None
        except:
            image = None

        link_tag = box.select_one(SELECTORS["link"])
        name_tag = box.select_one(SELECTORS["name"])
        price_tag = box.select_one(SELECTORS["price"])
        if price_tag:
            raw_price = price_tag.get_text(strip=True)
            price = int(re.sub(r'\D+', '', raw_price))
        else:
            price = None

        product = {
            "product_link": link_tag["href"] if link_tag else None,
            "image": image,
            "name": name_tag.get_text(strip=True) if name_tag else None,
            "price": price,
            "category_link": driver.current_url,
            "source": "jofogas",  # megmarad így, ahogy kérted
            "date": TODAY
        }
        items.append(product)

    return items

# ---- Scraper fő futtatás ----
def run_scraper():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    driver = setup_driver()
    driver.get(START_URL)

    # Cookie banner
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )
        cookie_btn.click()
    except:
        tqdm.write("ℹ️ Cookie gomb nem jelent meg vagy már el lett fogadva.")

    # Oldalszám meghatározása
    soup = BeautifulSoup(driver.page_source, "html.parser")
    page_info_tag = soup.select_one("div.text-center")
    if page_info_tag:
        title = page_info_tag.get("title", "")
        try:
            total_pages = int(title.split("/")[1].strip().split()[0])
        except (IndexError, ValueError):
            total_pages = 1
    else:
        total_pages = 1

    print(f"🔢 Összes oldal: {total_pages}")
    all_data = []

    with tqdm(total=total_pages, desc="📄 Vatera oldalak", unit="oldal") as pbar:
        for page in range(1, total_pages + 1):
            url = START_URL if page == 1 else f"{START_URL}?p={page}"
            driver.get(url)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["product_box"])))
            all_data.extend(extract_products_from_page(driver))
            pbar.update(1)

    driver.quit()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Kész: {len(all_data)} termék mentve → {OUTPUT_FILE}")

# ---- Indítás ----
if __name__ == "__main__":
    run_scraper()