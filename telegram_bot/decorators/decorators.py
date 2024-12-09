import requests

from config import settings, dp, bot, bot_settings
from functools import wraps
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, CallbackQuery
from states.states import WelcomeGiftStates
from keyboards.keyboards import HomeMenu
from typing import Any, Callable


def private_message(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[0]

        if message.chat.type == "private":

            return await func(
                *args, **kwargs
            )

    return wrapper

def handle_error(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[0]

        if message.from_user.id in bot_settings.BANNED_USERS:
            return await bot.send_message(
                chat_id=message.from_user.id,
                text="<b>Bot is unavailable.</b>",
                parse_mode="HTML"
            )

        try:
            return await func(
                *args, **kwargs
            )
        except Exception as err:
            print(f"WARNING | Error during {func} function execution with error: {err}")

    return wrapper

def check_pretzel_task(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(
            *args, **kwargs
    ) -> Any:
        callback: CallbackQuery = args[0]
        response = requests.get(
            url=f"{settings.BASE_API_URL}/user/{callback.from_user.id}/pretzels_task?task={callback.data}"
        )

        if response.status_code == 200:
            response_data = response.json()["data"]

            if not response_data["allowed"]:

                if response_data["task"] in ["retweet_post"]:
                    match response_data["status"]:
                        case "declined":

                            return await callback.answer(
                                text="⛔️ You missed the free Pretzel.",
                                show_alert=True
                            )

                        case "pending":

                            return await callback.answer(
                                text="️🌀 Your submission is still under review.",
                                show_alert=True
                            )

                return await callback.answer(
                    text="✅ You've completed this task.",
                    show_alert=True
                )

        return await func(
            *args, **kwargs
        )

    return wrapper

def check_payload(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(
            *args, **kwargs
    ) -> Any:
        message: Message = args[0]
        state = await (dp.current_state()).get_state()

        match state:
            case WelcomeGiftStates.username.state:
                if message.text[0] != "@":

                    return await message.answer(
                        text="<i>Invalid Username, please submit again.</i>",
                        reply_markup=HomeMenu.keyboard(),
                        parse_mode="HTML"
                    )

            case WelcomeGiftStates.profile_name.state:
                if message.text[:14] != "https://x.com/":

                    return await message.answer(
                        text="<i>Invalid Profile Name, please submit again.</i>",
                        reply_markup=HomeMenu.keyboard(),
                        parse_mode="HTML"
                    )

            case WelcomeGiftStates.retweet_name.state:
                if message.text[:14] != "https://x.com/":

                    return await message.answer(
                        text="<i>Invalid Profile Name, please submit again.</i>",
                        reply_markup=HomeMenu.keyboard(),
                        parse_mode="HTML"
                    )

        return await func(
            *args, **kwargs
        )

    return wrapper


def check_banned(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(
            *args, **kwargs
    ) -> Any:
        message: Message = args[0]

        if message.from_user.id in settings.BANNED_USERS:
            return await bot.send_message(
                chat_id=message.from_user.id,
                text="<b>Bot is unavailable.</b>",
                parse_mode="HTML"
            )
        return await func(
            *args, **kwargs
        )

    return wrapper


