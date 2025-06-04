#!/bin/bash

echo "🚀 Starte Produktchecker..."

# Versionsinfos loggen
echo "🧪 Chrome-Version:"
google-chrome --version || which google-chrome

echo "🧪 ChromeDriver-Version:"
chromedriver --version || which chromedriver

# Starte das Python-Skript
python main.py
