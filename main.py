import os
import time
import random
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Telegram Setup
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Produkt-URLs
PRODUCT_URLS = [
     "https://www.mueller.de/p/pokemon-sammelkartenspiel-super-premium-kollektion-karmesin-purpur-prismatische-entwicklungen-PPN3101975/?itemId=3101975",
    "https://www.mueller.de/p/pokemon-sammelkartenspiel-top-trainer-box-karmesin-purpur-prismatische-entwicklungen-IPN3074733/",
    "https://www.mueller.de/p/pokemon-sammelkartenspiel-spezial-kollektion-karmesin-purpur-prismatische-entwicklungen-zubehoer-beutel-PPN3098433/",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-super-premium-kollektion/p/250525",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-top-trainer-box/p/245332",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-ueberraschungsbox/p/246195",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten/pokemon-karten-karmesin-und-purpur-ewige-rivalen-top-trainer-box/p/250642",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten/pokemon-karmesin-und-purpur-ewige-rivalen-team-rockets-mewtu-ex-kollektion/p/250643",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten/pokemon-karten-karmesin-und-purpur-ewige-rivalen-3er-set-blister-sortiert/p/250623",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-45562-pokemon-kp035-booster-bundle-sammelkarten-2885370.html",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10617-pokemon-kp085-boosterbundle-sammelkarten-2973282.html",
    #"https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10598-pokemon-uberraschungsbox-fix6-karmesin-and-purpur-prismatische-entwicklungen-sammelkarten-2972604.html",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-11088-kp10-top-trainer-box-de-mbe4-sammelkarten-2988488.html",
    "https://www.mediamarkt.de/de/product/_pokemon-41094-team-rockets-mewtu-ex-kollekt-mbe6-sammelkarten-2988492.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11369-pkm-kp105-top-trainer-box-z-sammelkartenspiel-2992653.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11364-pkm-kp105-top-trainer-box-weiss-sammelkartenspiel-2992652.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11401-pkm-kp105-poster-kollektion-sammelkartenspiel-2992656.html",
     "https://www.mediamarkt.de/de/product/_pokemon-11396-pkm-kp105-ordner-kollekt-schwarz-sammelkartenspiel-2992655.html",
     "https://www.mediamarkt.de/de/product/_pokemon-11391-pkm-kp105-binder-collection-r-sammelkartenspiel-2992654.html",
    "https://www.pokemoncenter.com/product/100-10653/pokemon-tcg-scarlet-and-violet-destined-rivals-pokemon-center-elite-trainer-box",
    "https://www.pokemoncenter.com/product/100-10019/pokemon-tcg-scarlet-and-violet-prismatic-evolutions-pokemon-center-elite-trainer-box",
    "https://www.pokemoncenter.com/product/10-10027-101/pokemon-tcg-scarlet-and-violet-prismatic-evolutions-super-premium-collection"
    #test links
    #"https://www.pokemoncenter.com/product/70-10312-101/ralts-kirlia-gardevoir-and-mega-gardevoir-pokemon-pixel-pins-4-pack",
    #"https://www.mueller.de/p/pokemon-adventskalender-2021-2726315/",
    #"https://www.smythstoys.com/de/de-de/spielzeug/plueschtiere-und-kuscheltiere/kuscheltiere/pokemon-plueschtiere/pokemon-kuscheltier-glurak-30-cm/p/172049",
    #"https://www.mediamarkt.de/de/product/_the-pokemon-company-int-45935-pkm-kp07-stellarkrone-booster-sammelkarten-2951644.html"
]

CHECK_INTERVAL = 60 * 5  # 5 Minuten

# Telegram
def send_telegram_message(text):
    try:
        res = requests.get(TELEGRAM_API_URL, params={"chat_id": CHAT_ID, "text": text})
        if res.status_code != 200:
            print("[TELEGRAM] Fehler:", res.text)
    except Exception as e:
        print("[TELEGRAM] Ausnahme:", e)

# Chrome Setup
def get_chrome_driver():
    # Standardpfade passend zum Docker-Setup
    chrome_path = os.getenv("CHROME_PATH", "/usr/bin/chromium")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(executable_path=chromedriver_path)

    return webdriver.Chrome(service=service, options=chrome_options)



# Verfügbarkeitsprüfung
def is_product_available(url):
    try:
        if "smythstoys.com" in url or "pokemoncenter.com" in url:
            print(f"[INFO] Selenium-Prüfung: {url}")
            driver = get_chrome_driver()
            driver.get(url)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if "smythstoys.com" in url:
                print("[DEBUG] Suche Smyths-Button...")
                button = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'), 'in den warenkorb')]")
                for btn in button:
                    if btn.is_enabled() and "cursor-not-allowed" not in btn.get_attribute("class"):
                        print("[DEBUG] Smyths verfügbar.")
                        driver.quit()
                        return True

            if "pokemoncenter.com" in url:
                print("[DEBUG] Suche PokémonCenter-Button...")
                button = driver.find_elements(By.CLASS_NAME, "add-to-cart-button--PZmQF")
                for btn in button:
                    text = btn.text.strip().upper()
                    print(f"[DEBUG] Button-Text: {text}")
                    if "ADD TO CART" in text:
                        print("[DEBUG] PokémonCenter verfügbar.")
                        driver.quit()
                        return True

            driver.quit()
            print("[DEBUG] Kein aktiver Button gefunden.")
            return False

        else:
            print(f"[INFO] BeautifulSoup-Prüfung: {url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            button = soup.find(lambda tag:
                (tag.name == "button" or tag.name == "a") and
                "in den warenkorb" in tag.get_text(strip=True).lower())
            if button:
                return True

            not_available = soup.find(text=lambda t: t and "nicht verfügbar" in t.lower())
            return not not_available

    except Exception as e:
        print(f"[ERROR] Fehler bei {url}: {e}")
        return False

# Verfügbarkeitsüberwachung
def check_availability():
    send_telegram_message("🔎 Produktüberwachung gestartet!")
    while True:
        for url in PRODUCT_URLS:
            print(f"[CHECK] {url}")
            if is_product_available(url):
                send_telegram_message(f"✅ Verfügbar: {url}")
            else:
                print("[INFO] Nicht verfügbar.")
            time.sleep(random.uniform(1, 5))
        print(f"[WARTEN] Nächster Check in {CHECK_INTERVAL // 60} Minuten.")
        time.sleep(CHECK_INTERVAL)

# Heartbeat
def send_heartbeat():
    while True:
        send_telegram_message("⏰ Service läuft weiter.")
        time.sleep(3600)

# Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return "Produktüberwachung läuft."

@app.route("/health")
def health():
    return "OK"

# App-Start
if __name__ == "__main__":
    threading.Thread(target=check_availability, daemon=True).start()
    threading.Thread(target=send_heartbeat, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
