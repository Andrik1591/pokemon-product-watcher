import os
import time
import random  # NEU hinzugefügt
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Telegram Setup
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Produkt-URLs, die du überwachen willst
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
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10598-pokemon-uberraschungsbox-fix6-karmesin-and-purpur-prismatische-entwicklungen-sammelkarten-2972604.html",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-11088-kp10-top-trainer-box-de-mbe4-sammelkarten-2988488.html",
    "https://www.mediamarkt.de/de/product/_pokemon-41094-team-rockets-mewtu-ex-kollekt-mbe6-sammelkarten-2988492.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11369-pkm-kp105-top-trainer-box-z-sammelkartenspiel-2992653.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11364-pkm-kp105-top-trainer-box-weiss-sammelkartenspiel-2992652.html",
    "https://www.mediamarkt.de/de/product/_pokemon-11401-pkm-kp105-poster-kollektion-sammelkartenspiel-2992656.html",
    "https://www.mueller.de/p/pokemon-adventskalender-2021-2726315/",
    "https://www.smythstoys.com/de/de-de/spielzeug/plueschtiere-und-kuscheltiere/kuscheltiere/pokemon-plueschtiere/pokemon-kuscheltier-glurak-30-cm/p/172049",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-45935-pkm-kp07-stellarkrone-booster-sammelkarten-2951644.html"
]

CHECK_INTERVAL = 60 * 5  # alle 5 Minuten prüfen

def send_telegram_message(text):
    try:
        response = requests.get(TELEGRAM_API_URL, params={"chat_id": CHAT_ID, "text": text})
        if response.status_code != 200:
            print("Fehler beim Senden der Telegram-Nachricht:", response.text)
    except Exception as e:
        print("Exception beim Senden der Telegram-Nachricht:", e)

def is_product_available(url):
    try:
        if "smythstoys.com" in url:
            print("[INFO] Verwende Selenium für Smyths")

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # neues Headless-Modell (Chrome 109+)
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver.get(url)
            time.sleep(4)  # etwas länger warten, Ladezeiten können variieren

            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'), 'in den warenkorb')]"
            )
            print(f"[DEBUG] Smyths: Gefundene Buttons mit 'In den Warenkorb': {len(buttons)}")

            for btn in buttons:
                classlist = btn.get_attribute("class")
                is_disabled = btn.get_attribute("disabled") is not None
                aria_disabled = btn.get_attribute("aria-disabled") == "true"

                print(f"[DEBUG] Button-Klassen: {classlist}, disabled={is_disabled}, aria-disabled={aria_disabled}")

                # Prüfe deaktiviert/grau (disable oder aria-disabled) und Klassen
                if is_disabled or aria_disabled or "cursor-not-allowed" in classlist or "bg-grey" in classlist:
                    print("[DEBUG] Smyths: Button ist deaktiviert oder grau.")
                    continue

                # Prüfe ob Button grün (verfügbar)
                if "bg-green" in classlist or "bg-green-500" in classlist or "text-white" in classlist:
                    print("[DEBUG] Smyths: Grüner aktiver Button → Produkt verfügbar!")
                    driver.quit()
                    return True
                else:
                    print("[DEBUG] Smyths: Kein grüner Button – möglicherweise nicht verfügbar.")

            driver.quit()
            return False

        elif "mueller.de" in url or "mediamarkt.de" in url:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            if "mueller.de" in url:
                button = soup.find(lambda tag:
                                   (tag.name == "button" or tag.name == "a") and
                                   tag.get_text(strip=True).lower() == "in den warenkorb")
                return button is not None

            if "mediamarkt.de" in url:
                button = soup.find(lambda tag:
                                   (tag.name == "button" or tag.name == "a") and
                                   "in den warenkorb" in tag.get_text(strip=True).lower())
                if button:
                    return True
                not_available = soup.find(text=lambda t: t and "nicht verfügbar" in t.lower())
                return not not_available

        else:
            return False

    except Exception as e:
        print(f"Fehler beim Prüfen der URL {url}: {e}")
        return False

def check_availability():
    send_telegram_message("🔎 Produktüberwachung gestartet!")
    while True:
        for url in PRODUCT_URLS:
            print(f"Prüfe Verfügbarkeit: {url}")
            if is_product_available(url):
                send_telegram_message(f"✅ Produkt verfügbar: {url}")
            else:
                print("Nicht verfügbar.")

            delay = random.uniform(1, 5)
            print(f"Warte {delay:.2f} Sekunden vor dem nächsten Request...")
            time.sleep(delay)

        print(f"Warte {CHECK_INTERVAL / 60} Minuten bis zum nächsten Check.")
        time.sleep(CHECK_INTERVAL)

def send_heartbeat():
    while True:
        send_telegram_message("⏰ Service läuft noch - alles okay!")
        time.sleep(3600)

app = Flask(__name__)

@app.route("/")
def index():
    return "Produktüberwachung läuft!"

@app.route("/health")
def health_check():
    return "OK"

if __name__ == "__main__":
    thread_check = threading.Thread(target=check_availability)
    thread_check.daemon = True
    thread_check.start()

    thread_heartbeat = threading.Thread(target=send_heartbeat)
    thread_heartbeat.daemon = True
    thread_heartbeat.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
