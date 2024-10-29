from aiogram import executor
import random
import requests
import asyncio
from keyboards.keyboards import WithdrawMenu, HomeMenu
from config import dp, settings, bot
from handlers.events import register_events


register_events()

async def on_startup(_) -> None:
    print("Bot started")

async def on_shutdown(_) -> None:
    print("Bot shutdown")

if __name__ == "__main__":
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )