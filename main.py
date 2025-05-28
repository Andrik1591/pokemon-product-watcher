import os
import time
import random  # NEU hinzugefügt
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading 

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

        elif "smythstoys.com" in url:
            # Suche alle Buttons mit dem Text "In den Warenkorb"
            buttons = soup.find_all("button", string=lambda text: text and "in den warenkorb" in text.lower())

            print(f"[DEBUG] Smyths: Gefundene Buttons mit 'In den Warenkorb': {len(buttons)}")

            for btn in buttons:
                # Prüfe, ob Button deaktiviert ist
                classes = btn.get("class", [])
                aria_disabled = btn.get("aria-disabled", "").lower()
                if "disabled" in classes or aria_disabled == "true":
                    print("[DEBUG] Smyths: Button ist deaktiviert.")
                    continue

                # Prüfe, ob Button grün ist
                is_green = any(c.startswith("bg-green") for c in classes)
                if is_green:
                    print("[DEBUG] Smyths: Grüner aktiver Button → Produkt verfügbar!")
                    return True
                else:
                    print("[DEBUG] Smyths: Kein grüner Button – möglicherweise nicht verfügbar.")

            print("[DEBUG] Smyths: Kein aktiver grüner 'In den Warenkorb'-Button gefunden.")
            return False

        elif "mediamarkt.de" in url:
            button = soup.find(lambda tag:
                               (tag.name == "button" or tag.name == "a") and
                               "in den warenkorb" in tag.get_text(strip=True).lower())
            if button:
                return True
            not_available = soup.find(text=lambda t: t and "nicht verfügbar" in t.lower())
            return not not_available

        else:
            return response.status_code == 200

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
