import aiohttp
from config import CRYPTO_BOT_TOKEN

async def create_invoice(amount_rub: int, user_id: int) -> dict | None:
    # Получаем курс USDT/RUB через CryptoBot
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://pay.crypt.bot/api/v1/getMe",
            headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}
        ) as resp:
            if not resp.ok:
                return None

    amount_usdt = round(amount_rub / 100, 2)  # примерно, лучше запросить курс
    payload = {
        "asset": "USDT",
        "amount": amount_usdt,
        "description": f"Пополнение баланса #{user_id}",
        "payload": str(user_id)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pay.crypt.bot/api/v1/createInvoice",
            json=payload,
            headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}
        ) as resp:
            if resp.status == 200:
                return await resp.json()
    return None