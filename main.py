import requests
from bs4 import BeautifulSoup
import re  # Für regulären Ausdruck

def check_pokemoncenter_product(url):
    print(f"[INFO] Prüfe URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] HTTP Status Code: {response.status_code}")
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        print("[INFO] Suche nach Add-to-Cart-Button...")
        # Suche mit Regex-Klasse
        button = soup.find("button", class_=re.compile(r"add-to-cart-button"))

        if button:
            text = button.get_text(strip=True).upper()
            print(f"[DEBUG] Button-Text: '{text}'")
            if "ADD TO CART" in text:
                print("✅ Produkt ist VERFÜGBAR!")
            elif "SOLD OUT" in text or "UNAVAILABLE" in text:
                print("❌ Produkt ist NICHT verfügbar.")
            else:
                print("⚠️ Button-Text unklar.")
        else:
            print("❌ Kein Add-to-Cart-Button gefunden.")

    except Exception as e:
        print(f"[ERROR] Fehler beim Abrufen der Seite: {e}")

# Beispiel-URL (prüfe diese oder ersetze durch eine andere gültige)
test_url = "https://www.pokemoncenter.com/product/70-10312-101/ralts-kirlia-gardevoir-and-mega-gardevoir-pokemon-pixel-pins-4-pack"

check_pokemoncenter_product(test_url)
