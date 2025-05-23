import os
import time
import requests
from bs4 import BeautifulSoup

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
    "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10617-pokemon-kp085-boosterbundle-sammelkarten-2973282.html"
]

CHECK_INTERVAL = 60 * 10  # alle 10 Minuten prüfen

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

        # *** Anpassung je Shop ***

        # Mueller: Verfügbarkeit prüfen
        if "mueller.de" in url:
            # Beispiel: Button oder Text "Nicht verfügbar" prüfen
            not_available = soup.find(text=lambda t: "nicht verfügbar" in t.lower())
            if not not_available:
                return True
            else:
                return False

        # SmythsToys: Prüfen auf "Momentan nicht verfügbar" oder ähnliches
        elif "smythstoys.com" in url:
            not_available = soup.find(text=lambda t: "momentan nicht verfügbar" in t.lower())
            if not not_available:
                return True
            else:
                return False

        # MediaMarkt: Prüfen auf "nicht verfügbar"
        elif "mediamarkt.de" in url:
            not_available = soup.find(text=lambda t: "nicht verfügbar" in t.lower())
            if not not_available:
                return True
            else:
                return False

        else:
            # Für andere Shops einfach auf Statuscode achten (z.B. 200 = verfügbar)
            return response.status_code == 200

    except Exception as e:
        print(f"Fehler beim Prüfen der URL {url}: {e}")
        return False

def main():
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

if __name__ == "__main__":
    main()
