from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from db import get_pending_payment, update_balance, delete_pending_payment
from config import CRYPTO_BOT_TOKEN
import hashlib
import hmac
import logging

app = FastAPI()
logger = logging.getLogger("cryptobot_webhook")

@app.post("/webhook/cryptobot")
async def cryptobot_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Crypto-Pay-Signature")
    
    # Проверка подписи
    computed_signature = hmac.new(
        CRYPTO_BOT_TOKEN.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != computed_signature:
        return Response(status_code=400)

    data = await request.json()
    if data.get("type") != "invoice_paid":
        return JSONResponse({"ok": True})

    invoice = data["payload"]
    invoice_id = str(invoice["invoice_id"])
    user_id = int(invoice["payload"])  # мы передали user_id как payload
    amount_rub = int(float(invoice["amount"]) * 100)  # обратно в рубли (примерно)

    pending = await get_pending_payment(invoice_id)
    if not pending:
        logger.warning(f"Неизвестный счёт: {invoice_id}")
        return JSONResponse({"ok": True})

    await update_balance(user_id, amount_rub)
    await delete_pending_payment(invoice_id)
    logger.info(f"✅ Пополнение: {user_id} +{amount_rub} руб")

    return JSONResponse({"ok": True})