from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_pokemoncenter_product_selenium(url):
    print(f"[INFO] Prüfe mit Selenium URL: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "button"))
        )
        print("[INFO] Seite geladen. Suche nach Add-to-Cart-Button...")

        buttons = driver.find_elements(By.CLASS_NAME, "add-to-cart-button--PZmQF")

        if not buttons:
            print("❌ Kein Add-to-Cart-Button gefunden.")
        else:
            for btn in buttons:
                text = btn.text.strip().upper()
                print(f"[DEBUG] Button-Text: '{text}'")
                if "ADD TO CART" in text:
                    print("✅ Produkt ist VERFÜGBAR!")
                    break
            else:
                print("❌ Kein verfügbarer Button gefunden.")
    except Exception as e:
        print(f"[ERROR] Fehler mit Selenium: {e}")
    finally:
        driver.quit()

# Test
test_url = "https://www.pokemoncenter.com/product/70-10312-101/ralts-kirlia-gardevoir-and-mega-gardevoir-pokemon-pixel-pins-4-pack"
check_pokemoncenter_product_selenium(test_url)
