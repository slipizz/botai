from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_servers, add_server, delete_server
from keyboards import server_list_inline, cancel_kb

router = Router()

class ServerEdit(StatesGroup):
    name = State()
    host_url = State()
    username = State()
    password = State()
    inbound_id = State()
    price = State()

@router.message(F.text == "🖥 Сервера")
async def show_servers(message: Message):
    servers = await get_servers()
    if not servers:
        await message.answer("Нет серверов.")
    else:
        await message.answer("Сервера:", reply_markup=server_list_inline(servers))

@router.callback_query(F.data == "add_srv")
async def add_srv_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Название:", reply_markup=cancel_kb())
    await state.set_state(ServerEdit.name)
    await callback.answer()

# ... остальные шаги (аналогично предыдущему примеру)

@router.callback_query(F.data.startswith("edit_srv:"))
async def edit_srv_menu(callback: CallbackQuery):
    name = callback.data.split(":")[1]
    await callback.message.edit_text(
        f"Сервер: {name}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_srv:{name}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_srvs")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("del_srv:"))
async def del_srv(callback: CallbackQuery):
    name = callback.data.split(":")[1]
    await delete_server(name)
    await callback.message.edit_text("✅ Удалён.")
    await callback.answer()