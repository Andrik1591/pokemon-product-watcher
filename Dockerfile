# Basis-Image
FROM python:3.10-slim

# Installationen: Chromium + Selenium-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    chromium chromium-driver \
    fonts-liberation libappindicator3-1 libasound2 libnspr4 libnss3 libxss1 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Umgebungsvariablen für Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$CHROME_BIN:$PATH"

# Arbeitsverzeichnis
WORKDIR /app

# Projektdateien kopieren
COPY . .

# Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Startkommando
CMD ["bash", "start.sh"]
