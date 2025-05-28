#!/bin/bash
set -e

# Update und benötigte Tools installieren
apt-get update
apt-get install -y wget gnupg

# Google Chrome Signing Key hinzufügen
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Google Chrome Repo hinzufügen
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Chrome installieren
apt-get update
apt-get install -y google-chrome-stable

# Berechtigungen setzen
chmod +x /usr/bin/google-chrome
