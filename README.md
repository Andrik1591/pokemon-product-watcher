# Pokemon Produktverfügbarkeits-Notifier

Dieses Projekt überwacht die Verfügbarkeit von Pokemon-Produkten auf verschiedenen Webseiten und sendet dir bei Verfügbarkeit eine Telegram-Nachricht.

## Einrichtung

1. `.env` Datei anlegen mit:
   ```
   TELEGRAM_BOT_TOKEN=dein_token
   TELEGRAM_CHAT_ID=deine_chat_id
   ```

2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

3. Bot starten:
   ```
   python main.py
   ```

## Railway Deployment

1. Repo auf GitHub hochladen.
2. Mit Railway verbinden.
3. `.env`-Werte als Railway Secrets eintragen.
4. Starten – fertig!