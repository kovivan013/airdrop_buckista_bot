from aiogram import executor
import asyncio
from config import dp
from handlers.events import register_events


register_events()

async def check_transfers():
    while True:
        print("Задача выполняется...")
        await asyncio.sleep(5)

async def on_startup(_) -> None:
    asyncio.create_task(
        check_transfers()
    )
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