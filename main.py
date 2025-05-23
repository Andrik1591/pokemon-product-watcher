import os
import time
import requests
from bs4 import BeautifulSoup
import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("8192859743:AAF6goMe43JLcIWr9h6aCZRD695oQFsq3ck")
TELEGRAM_CHAT_ID = os.getenv("6092740808")

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

products = [
    {
        "name": "Pokemon Super Premium Kollektion",
        "url": "https://www.mueller.de/p/pokemon-sammelkartenspiel-super-premium-kollektion-karmesin-purpur-prismatische-entwicklungen-PPN3101975/?itemId=3101975"
    },
    {
        "name": "Pokemon Top Trainer Box",
        "url": "https://www.mueller.de/p/pokemon-sammelkartenspiel-top-trainer-box-karmesin-purpur-prismatische-entwicklungen-IPN3074733/"
    },
    {
        "name": "Pokemon Spezial Kollektion Zubehör-Beutel",
        "url": "https://www.mueller.de/p/pokemon-sammelkartenspiel-spezial-kollektion-karmesin-purpur-prismatische-entwicklungen-zubehoer-beutel-PPN3098433/"
    },
    {
        "name": "Pokemon Smyths Super Premium Kollektion",
        "url": "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-super-premium-kollektion/p/250525"
    },
    {
        "name": "Pokemon Smyths Top Trainer Box",
        "url": "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-top-trainer-box/p/245332"
    },
    {
        "name": "Pokemon Smyths Überraschungsbox",
        "url": "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/pokemon/pokemon-karten-karmesin-und-purpur-prismatische-entwicklungen-ueberraschungsbox/p/246195"
    },
    {
        "name": "Pokemon MediaMarkt Boosterbundle",
        "url": "https://www.mediamarkt.de/de/product/_the-pokemon-company-int-10617-pokemon-kp085-boosterbundle-sammelkarten-2973282.html"
    },
]

def check_availability(product):
    try:
        resp = requests.get(product["url"], timeout=10)
        resp.raise_for_status()
        if ("ausverkauft" in resp.text.lower()) or ("nicht verfügbar" in resp.text.lower()):
            return False
        return True
    except Exception as e:
        print(f"Fehler bei {product['name']}: {e}")
        return False

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print(f"Nachricht gesendet: {text}")
    except Exception as e:
        print(f"Telegram Fehler: {e}")

def main():
    notified = set()
    while True:
        for product in products:
            available = check_availability(product)
            if available and product["url"] not in notified:
                msg = f"✅ VERFÜGBAR: {product['name']}\n{product['url']}"
                send_telegram_message(msg)
                notified.add(product["url"])
            else:
                print(f"Nicht verfügbar: {product['name']}")
        time.sleep(300)

if __name__ == "__main__":
    main()