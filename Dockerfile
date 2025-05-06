FROM python:3.9.22

# Set working directory
WORKDIR /Musical_Bot

# Install system dependencies (including Chromium and ChromeDriver)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make sure pip is up to date
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code into the image
COPY . .

# Set display port to avoid errors
ENV DISPLAY=:99

# Set Telegram bot port (optional, only useful for webhooks or Railway logs)
ENV PORT=9000
EXPOSE 9000

# Start the bot
CMD ["python", "Telegram_Bot.py"]