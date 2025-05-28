#!/bin/bash
# Chromium installieren
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# (Optional) Link setzen, falls nötig
ln -s /usr/bin/chromium-browser /usr/bin/google-chrome

# 2. Abhängigkeiten installieren
pip install -r requirements.txt
