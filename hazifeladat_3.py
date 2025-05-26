from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from datetime import datetime
import json
import pandas as pd

# 🧭 Egyszerűsített, tiszta szelektorok
selectors = {
    "product_box": "a[href^='/shop/termek/']",
    "image": "img",
    "name": "h3",
    "price": "h4",
    "next_page_button": 'button.pagination-next', # A legutóbbi kép alapján
    "cookie_accept_button": '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll' # A legfrissebb HTML alapján
}

# 🔧 Selenium indítása
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless=new") # Ha nem akarsz grafikus felületet, vedd ki kommentből ezt
driver = webdriver.Chrome(options=options)

# 🌐 Oldal betöltése
url = "https://ipon.hu/kereses/shop?keyword=notebook"
driver.get(url)

# --- Süti ablak kezelése ---
try:
    # Várjuk meg, amíg a süti ablak gombja megjelenik és kattinthatóvá válik
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["cookie_accept_button"]))
    )
    cookie_button.click()
    print("Süti elfogadó gombra kattintva.")
    time.sleep(2) # Rövid várakozás, amíg a süti ablak eltűnik
except TimeoutException:
    print("Süti elfogadó gomb nem található vagy nem kattintható 10 másodpercen belül (talán már elfogadva).")
except ElementClickInterceptedException:
    print("Süti gombra kattintás elkapva, valószínűleg másik elem takarja.")
    # Ezen a ponton szükség lehet manuális hibakeresésre, ha mégsem tűnik el az akadályozó elem.
except Exception as e:
    print(f"Hiba a süti ablak kezelésekor: {e}")
# ---------------------------

# Adatgyűjtéshez szükséges lista
all_products_data = []
pozicio_counter = 1 # A termék pozíciójának számlálója az összes oldalon keresztül

while True:
    print(f"--- Oldal betöltése ---")
    
    # Várjuk meg, amíg a termékkártyák megjelennek.
    try:
        WebDriverWait(driver, 15).until( # Növeltük a várakozási időt 15 másodpercre
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selectors["product_box"]))
        )
    except TimeoutException:
        print(f"Nincsenek termékek az oldalon 15 másodpercen belül, feltételezhetően az utolsó oldalon vagyunk vagy hiba történt.")
        break
    except Exception as e:
        print(f"Hiba a termékek betöltésekor az oldalon: {e}")
        break 

    # 📦 Termékkártyák kiválasztása
    product_cards = driver.find_elements(By.CSS_SELECTOR, selectors["product_box"])
    print(f"🔍 Talált termékdobozok száma az aktuális oldalon: {len(product_cards)}")

    if not product_cards: # Ha nincsenek termékkártyák az oldalon, akkor valószínűleg vége
        print("Nincsenek termékek az oldalon, feltételezhetően az utolsó oldalon vagyunk.")
        break

    for card in product_cards:
        try:
            # Ellenőrizzük, hogy a kártya tartalmaz-e releváns adatokat
            name_element = card.find_elements(By.CSS_SELECTOR, selectors["name"])
            price_element = card.find_elements(By.CSS_SELECTOR, selectors["price"])

            if not (name_element and price_element):
                #print("Skipping a card without name or price.") 
                continue

            product_link = card.get_attribute("href")
            image_element = card.find_elements(By.CSS_SELECTOR, selectors["image"])
            image = image_element[0].get_attribute("data-img") if image_element else ""

            name = name_element[0].text.strip()
            price_text = card.find_element(By.CSS_SELECTOR, selectors["price"]).text.strip()
            # Ár tisztítása és számmá alakítása (szóközök eltávolítása, csak számjegyek megtartása)
            price = int(''.join(filter(str.isdigit, price_text))) if price_text else None

            category_link = driver.current_url
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            product_data = {
                "product_link": product_link,
                "category_link": category_link,
                "image": image,
                "name": name,
                "price": price,
                "pozicio": pozicio_counter,
                "time": time_now
            }
            all_products_data.append(product_data)
            pozicio_counter += 1

        except Exception as e:
            print(f"⚠️ Hiba termék feldolgozásánál (pozíció: {pozicio_counter}): {e}")
            continue

    # Lapozás
    try:
        # Várjuk meg, amíg a következő oldal gombja megjelenik és kattinthatóvá válik
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["next_page_button"]))
        )

        # Ellenőrizzük, hogy a gomb inaktív-e a 'disabled' attribútum alapján
        if next_page_button.get_attribute("disabled"):
             print("Nincs több oldal a lapozáshoz (a gomb inaktív, 'disabled' attribútummal).")
             break
        
        next_page_button.click()
        print("Kattintás a következő oldalra...")
        time.sleep(2) # Rövid várakozás a következő oldal betöltésére
    except TimeoutException:
        print("Nincs több oldal a lapozáshoz (nem található a következő oldal gomb 10 másodpercen belül).")
        break 
    except Exception as e:
        print(f"Hiba a lapozás során: {e}")
        break 

# 🚪 Lezárás
driver.quit()

# 💾 Adatok mentése JSON fájlba
output_json_file = "ipon_notebooks.json"
with open(output_json_file, 'w', encoding='utf-8') as f:
    json.dump(all_products_data, f, ensure_ascii=False, indent=4)
print(f"Adatok mentve a '{output_json_file}' fájlba.")

# 📊 Adatok exportálása Excelbe
df = pd.DataFrame(all_products_data)

# Az XLSX template oszlopneveinek megfeleltetése
df = df.rename(columns={
    'product_link': 'A termék ipon.hu linkje',
    'category_link': 'A gyűjtőoldal linkje',
    'image': 'A termékkép src-je (megnyitható url)',
    'name': 'A termék neve',
    'price': 'A termék ára, egyszerű szám',
    'pozicio': 'Pozíció', 
    'time': 'Az adatgyűjtés időpontja'
})

output_excel_file = "ipon_notebooks.xlsx"
df.to_excel(output_excel_file, index=False)
print(f"Adatok exportálva a '{output_excel_file}' Excel fájlba.")