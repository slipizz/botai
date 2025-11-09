from aiogram import Router, F
from aiogram.types import Message
from db import get_user_keys, get_balance
from xui_manager import get_key_details_from_host

router = Router()

@router.message(F.text == "👛 Баланс")
async def balance(message: Message):
    bal = await get_balance(message.from_user.id)
    await message.answer(f"Ваш баланс: {bal} руб.")

@router.message(F.text == "🔑 Мои подписки")
async def my_keys(message: Message):
    keys = await get_user_keys(message.from_user.id)
    if not keys:
        await message.answer("Нет активных подписок.")
        return
    for k in keys:
        key_data = {"host_name": k[2], "xui_client_uuid": k[4], "email": k[1]}
        res = await get_key_details_from_host(key_data)
        if res and res.get("connection_string"):
            await message.answer(f"<code>{res['connection_string']}</code>", parse_mode="HTML")
        else:
            await message.answer(f"Подписка на {k[2]} недоступна.")