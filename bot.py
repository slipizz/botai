import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_DOMAIN, WEBHOOK_PATH
from db import init_db
from handlers import setup_handlers
from webhooks import app as webhook_app

logging.basicConfig(level=logging.INFO)

WEBHOOK_URL = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    await init_db()
    logging.info("Бот запущен с вебхуком")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)

def main():
    setup_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(webhook_app, path=WEBHOOK_PATH)

    # Запуск FastAPI + aiohttp
    uvicorn.run(
        webhook_app,
        host=WEB_SERVER_HOST,
        port=WEB_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()