from aiogram import Dispatcher
from config import settings
from utils import utils
import requests
from decorators.decorators import private_message, handle_error
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


access_states = [
    AdminStates.admin_panel,
    AdminStates.overview,
    AdminStates.user_data,
    AdminStates.lucky_user,
    AdminStates.lucky_amount,
    AdminStates.top_referrers
]

@handle_error
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

@handle_error
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

@handle_error
async def overview(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.overview.set()
    response = requests.get("http://127.0.0.1:8000/admin/overview").json()["data"]
    await event.message.answer(
        text="📊 Overview\n"
             "\n"
             f"👥 Total users: {response['total_users']}\n"
             f"👥 Total Registered Users: {response['registered_users']}\n"
             f"👥 Today: {response['registered_today']}\n"
             "\n"
             f"✅ Total Completed Tasks: {response['total_completed_tasks']}\n"
             f"✅ Total Referrals: {response['total_refferals']}\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def enter_user_id(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.user_data.set()
    await event.message.answer(
        text="📊 User Data\n"
             "\n"
             "Enter the UserID of the user",
        parse_mode="Markdown"
    )

@handle_error
async def user_data(
        event: Message,
        state: FSMContext
) -> None:
    await event.answer(
        text="📊 User Data\n"
             "\n"
             "UserID: 5247144609\n"
             "Username: @marc_ivy\n"
             "Completed Tasks: 2 / 1\n"
             "Friends Referred: 8\n"
             "Current Balance: 0 USDT\n"
             "Withdrawal Request: 1.6 USDT\n"
             "Total Withdrawals: 3.5 USDT",
        reply_markup=HomeMenu.keyboard(),
    )

@handle_error
async def lucky_draw_user(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.lucky_user.set()
    await event.message.answer(
        text="🎰 Lucky Draw\n"
             "\n"
             "Enter the UserID of the user\n",
        parse_mode="Markdown"
    )

@handle_error
async def lucky_draw_amount(
        event: Message,
        state: FSMContext
) -> None:
    await AdminStates.lucky_amount.set()
    await event.answer(
        text="🎰 Lucky Draw\n"
             "\n"
             "Enter the prize amount for the user with ID 1122236574\n",
        parse_mode="Markdown"
    )

@handle_error
async def lucky_draw(
        event: Message,
        state: FSMContext
) -> None:
    await event.answer(
        text="✅ The user with ID 1122236574 has successfully received a prize of 200 USDT.\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode='Markdown'
    )

@handle_error
async def top_referrers(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.top_referrers.set()
    await event.message.answer(
        text="🏆 Top Referrers\n"
             "\n"
             "UserID / Username / Friends Referred\n"
             "5247144609 / @marc_ivy / 1221\n"
             "1134578922 / @dddyyuy / 1090\n"
             "1044448843 / @ttu88er / 890\n"
             "89456732 / @yyuuud / 764\n"
             "7777777222 / @hut / 478\n"
             "4587393445 / @jookertu / 475\n"
             "294872983 / @77sdy4 / 248\n"
             "3829238933 / @hhhhhrrrr / 188\n"
             "3388444555 / @hi_ert / 94\n"
             "117345565 / @___dddi1 / 17\n",
        reply_markup=HomeMenu.keyboard(),
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
    dp.register_callback_query_handler(
        overview,
        Text(
            equals=AdminMenu.overview_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        enter_user_id,
        Text(
            equals=AdminMenu.user_data_callback
        ),
        state=access_states
    )
    dp.register_message_handler(
        user_data,
        state=AdminStates.user_data
    )
    dp.register_callback_query_handler(
        lucky_draw_user,
        Text(
            equals=AdminMenu.lucky_draw_callback
        ),
        state=access_states
    )
    dp.register_message_handler(
        lucky_draw_amount,
        state=AdminStates.lucky_user
    )
    dp.register_message_handler(
        lucky_draw,
        state=AdminStates.lucky_amount
    )
    dp.register_callback_query_handler(
        top_referrers,
        Text(
            equals=AdminMenu.top_referrers_callback
        ),
        state=access_states
    )