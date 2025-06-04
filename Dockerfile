FROM python:3.10-slim

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip fonts-liberation \
    libappindicator3-1 libasound2 libnspr4 libnss3 libxss1 libxtst6 \
    libatk-bridge2.0-0 libc6 libcairo2 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libxext6 libxfixes3 libglib2.0-0 \
    libgbm1 libdbus-1-3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome installieren
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Passenden ChromeDriver installieren
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Env-Variablen setzen, passend zu deinem Python-Code
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "start.sh"]
