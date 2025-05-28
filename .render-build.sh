#!/usr/bin/env bash

# Chrome installieren (Headless)
curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb
apt-get update
apt-get install -y ./chrome.deb
rm chrome.deb

# ChromeDriver passend zur Chrome-Version holen
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
