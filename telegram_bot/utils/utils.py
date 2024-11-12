import hashlib
import requests
from datetime import datetime
import pytz

from decorators.decorators import handle_error
from config import settings, bot
from keyboards.keyboards import HomeMenu
from aiogram.types import Message


def hash(string: str) -> str:
    hash = hashlib.sha384()
    hash.update(
        bytes(
            string,
            "utf-8"
        )
    )
    return hash.hexdigest()

def from_timestamp(
        timestamp: int,
        timezone: str = "CET"
) -> str:
    utc_time = datetime.fromtimestamp(timestamp, pytz.UTC)
    tz = pytz.timezone(timezone)
    local_time = utc_time.astimezone(tz)
    string = local_time.strftime("%b %d, %I %p ") + timezone

    return string


@handle_error
async def accept_join_task(
        task_id: str,
        admin_id: int
) -> None:
    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/approve_pretzel_task?admin_id={admin_id}&task_id={task_id}"
    ).json()

    if response["status"] == 200:
        response_data = response["data"]

        await bot.send_message(
            chat_id=response_data["user_id"],
            text=f"🎉 <b>Congratulations!</b> \n"
                 f"\n"
                 f"You received a reward of <b>{response_data['reward']} Pretzel{'s' if response_data['reward'] > 1 else ''}</b>\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )


@handle_error
async def decline_join_task(
        task_id: str,
        admin_id: int
) -> None:
    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/decline_pretzel_task?admin_id={admin_id}&task_id={task_id}"
    ).json()

    if response["status"] == 200:
        response_data = response["data"]

        await bot.send_message(
            chat_id=response_data["user_id"],
            text="🙅 <b>Welcome Gift Declined</b>\n"
                 "\n"
                 "You have not joined the <a href='https://t.me/mrbuckista'>channel</a> yet. Please try again.\n",
            disable_web_page_preview=True,
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )
