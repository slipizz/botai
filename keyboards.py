from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👛 Баланс")],
            [KeyboardButton(text="🔑 Мои подписки")],
            [KeyboardButton(text="➕ Купить подписку")],
            [KeyboardButton(text="💰 Пополнить")],
            [KeyboardButton(text="🎁 Промокод")],
        ],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Управление пользователями")],
            [KeyboardButton(text="🖥 Сервера")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🎟 Промокоды")],
        ],
        resize_keyboard=True
    )

def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def server_list_inline(servers):
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"edit_srv:{name}")] for name, _ in servers]
    buttons.append([InlineKeyboardButton(text="➕ Добавить сервер", callback_data="add_srv")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)