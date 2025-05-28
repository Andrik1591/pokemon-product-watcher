#!/bin/bash

# Chrome installieren auf Render (Debian/Ubuntu Basis)
apt-get update
apt-get install -y wget unzip fontconfig locales

# Chrome Stable herunterladen und installieren
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Chrome-Treiber für Selenium
CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Aufräumen
rm google-chrome-stable_current_amd64.deb
rm chromedriver_linux64.zip

echo "Chrome und ChromeDriver wurden installiert."
