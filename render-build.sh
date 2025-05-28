#!/bin/bash

# Chromium + ChromeDriver installieren
apt-get update
apt-get install -y wget unzip curl gnupg

# Google Chrome installieren
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Symlink setzen (falls Selenium nach chromium-browser sucht)
ln -s /usr/bin/google-chrome /usr/bin/chromium-browser || true

# ChromeDriver passend installieren
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1)
DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
wget -N "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip -d /usr/bin
chmod +x /usr/bin/chromedriver

# Python-Abhängigkeiten installieren
pip install -r requirements.txt
