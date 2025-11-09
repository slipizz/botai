import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))

# CryptoBot
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN", "YOUR_CRYPTO_BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN", "https://yourdomain.com")  # без слэша в конце
WEBHOOK_PATH = "/webhook/cryptobot"

# YooMoney (ручной)
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "4100112233445566")