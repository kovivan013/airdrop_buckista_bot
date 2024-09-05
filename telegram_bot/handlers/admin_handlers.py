from aiogram import Dispatcher
from config import settings
from utils import utils

from aiogram.types import (
    Message,
    CallbackQuery
)
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from states.states import (
    AdminStates
)
from keyboards.keyboards import (
    HomeMenu,
    AdminMenu
)


async def check_admin(
        event: Message,
        state: FSMContext
) -> None:
    await AdminStates.enter_password.set()
    await event.answer(
        text="*Enter admin password:*",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )


async def admin_menu(
        event: Message,
        state: FSMContext
) -> None:
    password_hash = utils.hash(
        event.text
    )
    if settings.ADMIN_PASSWORD != password_hash:
        return await event.answer(
            text="*Incorrect password, please try again.*",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )
    await AdminStates.admin_panel.set()
    await event.answer(
        text="*You have successfully logged in as an administrator.*",
        reply_markup=AdminMenu.keyboard(),
        parse_mode="Markdown"
    )


def register(
        dp: Dispatcher
) -> None:
    dp.register_message_handler(
        check_admin,
        commands=["admin"]
    )
    dp.register_message_handler(
        admin_menu,
        state=AdminStates.enter_password
    )