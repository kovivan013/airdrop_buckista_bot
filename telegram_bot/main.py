from aiogram import executor
import random
import requests
import asyncio
from keyboards.keyboards import WithdrawMenu
from config import dp, settings, bot
from handlers.events import register_events

# DEPLOY UPDATE HELPERS CHAT, TEST_WITHDRAWALS, IP ADDRESS

register_events()

async def check_transfers():
    while True:
        await asyncio.sleep(5)
        response = requests.post(
            url=f"{settings.BASE_API_URL}/admin/transfer",
            json={
                "token": settings.CRYPTOBOT_TOKEN
            }
        )

        if response.status_code == 200 and response.json()["status"] == 200:

            print(response.json())

            for i, v in response.json()["data"].items():
                if v["message_id"]:
                    withdrawal_data = v["request"]
                    if v["status"] == "sent":
                        try:
                            await bot.edit_message_text(
                                chat_id=settings.ADMINS_CHAT,
                                message_id=v['message_id'],
                                text="✅ <b>Withdrawal Request Approved</b>\n"
                                     "\n"
                                     f"<b>User ID</b>: {withdrawal_data['user_id']}\n"
                                     f"<b>Username</b>: {withdrawal_data['username']}\n"
                                     # f"<b>TON Wallet Address</b>: {withdrawal_data['ton_address']}\n"
                                     f"<b>Requested Balance</b>: {withdrawal_data['amount']} USDT\n"
                                     f"\n"
                                     f"<b>Payment status</b>: Sent\n"
                                     f"<b>Last activity</b>: {v['updated_at'] + random.randint(1, 10)}",
                                reply_markup={},
                                parse_mode="HTML"
                            )
                        except:
                            pass
                    elif v["status"] == "failed":
                        requests.patch(
                            url=f"{settings.BASE_API_URL}/reset_withdrawal?withdrawal_id={withdrawal_data['id']}"
                        )
                        try:
                            await bot.edit_message_text(
                                chat_id=settings.ADMINS_CHAT,
                                message_id=v['message_id'],
                                text="🆕 <b>New Withdrawal Request</b>\n"
                                     "\n"
                                     f"<b>User ID</b>: {withdrawal_data['user_id']}\n"
                                     f"<b>Username</b>: {withdrawal_data['username']}\n"
                                     # f"<b>TON Wallet Address</b>: {withdrawal_data['ton_address']}\n"
                                     f"<b>Requested Balance</b>: {withdrawal_data['amount']} USDT\n"
                                     f"\n"
                                     f"<b>Payment status</b>: Failed\n"
                                     f"<b>Last activity</b>: {v['updated_at'] + random.randint(1, 10)}",
                                reply_markup=WithdrawMenu.control(
                                    withdrawal_id=withdrawal_data["id"]
                                ),
                                parse_mode="HTML"
                            )
                        except:
                            pass



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