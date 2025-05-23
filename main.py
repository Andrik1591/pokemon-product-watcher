import os
import time
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
    "https://www.mueller.de/p/lego-star-wars-75375-millennium-falcon-bauset-IPN2962320/",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-super-premium-kollektion/p/250525",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-top-trainer-box/p/245332",
    "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-ueberraschungsbox/p/246195",
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10617-pokemon-kp085-boosterbundle-sammelkarten-2973282.html"
]

CHECK_INTERVAL = 60  # jede Minute prüfen

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Mueller: Suche Button oder Link mit Text "In den Warenkorb"
        if "mueller.de" in url:
            # Suche Buttons und Links mit dem Text
            button = soup.find(lambda tag: 
                               (tag.name == "button" or tag.name == "a") and
                               tag.get_text(strip=True).lower() == "in den warenkorb")
            return button is not None

        # SmythsToys: Prüfen auf "Momentan nicht verfügbar" oder ähnliches
        elif "smythstoys.com" in url:
            not_available = soup.find(text=lambda t: t and "momentan nicht verfügbar" in t.lower())
            return not not_available

        # MediaMarkt: Prüfen auf "nicht verfügbar"
        elif "mediamarkt.de" in url:
            not_available = soup.find(text=lambda t: t and "nicht verfügbar" in t.lower())
            return not not_available

        else:
            # Für andere Shops einfach auf Statuscode achten (z.B. 200 = verfügbar)
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
        print(f"Warte {CHECK_INTERVAL/60} Minuten bis zum nächsten Check.")
        time.sleep(CHECK_INTERVAL)

app = Flask(__name__)

@app.route("/")
def index():
    return "Produktüberwachung läuft!"

if __name__ == "__main__":
    # Starte deine Überwachungsfunktion als Thread
    thread = threading.Thread(target=check_availability)
    thread.daemon = True
    thread.start()

    # Starte den Webserver
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
