import os
import requests

def send_test_message():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message = "🚀 Bot gestartet und läuft!"
    params = {"chat_id": chat_id, "text": message}
    try:
        response = requests.get(url, params=params)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    send_test_message()
