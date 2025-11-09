from aiogram import Dispatcher
from . import user, admin, payments, promo_ref

def setup_handlers(dp: Dispatcher):
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(payments.router)
    dp.include_router(promo_ref.router)