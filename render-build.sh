#!/bin/bash

# System vorbereiten
apt-get update
apt-get install -y wget unzip curl gnupg apt-transport-https software-properties-common

# Google Chrome installieren
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# ChromeDriver installieren
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1)
DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
wget -N "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
mv -f chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Chromium-Fallback-Link setzen
ln -sf /usr/bin/google-chrome /usr/bin/chromium-browser

# Python dependencies installieren
pip install -r requirements.txt
