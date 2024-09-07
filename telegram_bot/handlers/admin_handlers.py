from aiogram import Dispatcher
from config import settings, bot
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
    AdminMenu,
    WithdrawMenu
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

# @handle_error
async def user_data(
        event: Message,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"http://127.0.0.1:8000/user/{event.text}"
    ).json()

    if response["status"] == 200:
        current_withdrawal = requests.get(
            url=f"http://127.0.0.1:8000/user/current_withdrawal?withdrawal_id={response['data']['current_withdrawal']}"
        ).json()
        total_withdrawals = requests.get(
            url=f"http://127.0.0.1:8000/user/{event.text}/total_withdrawals"
        ).json()["data"]
        return await event.answer(
            text="📊 User Data\n"
                 "\n"
                 f"UserID: {response['data']['telegram_id']}\n"
                 f"Username: {'@' + response['data']['username'] if response['data']['username'] else 'None'}\n"
                 f"Completed Tasks: {len([i for i in response['data']['completed_tasks'].values() if i])} / 1\n"
                 f"Friends Referred: {len(response['data']['referred_friends'])}\n"
                 f"Current Balance: {response['data']['balance']} USDT\n"
                 f"Withdrawal Request: {current_withdrawal['data']['amount'] if current_withdrawal['status'] == 200 else 0} USDT\n"
                 f"Total Withdrawals: {total_withdrawals['total_withdrawals']} USDT",
            reply_markup=HomeMenu.keyboard(),
        )

    await event.answer(
        text=response["message"],
        reply_markup=HomeMenu.keyboard()
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
    async with state.proxy() as data:
        data["user_id"] = int(
            event.text
        )
    await event.answer(
        text="🎰 Lucky Draw\n"
             "\n"
             f"Enter the prize amount for the user with ID {event.text}\n",
        parse_mode="Markdown"
    )

@handle_error
async def lucky_draw(
        event: Message,
        state: FSMContext
) -> None:
    async with state.proxy() as data:

        response = requests.put(
            url=f"http://127.0.0.1:8000/user/{data['user_id']}/increase_balance?amount={event.text}"
        ).json()

        if response["status"] == 200:

            await event.answer(
                text=f"✅ The user with ID {data['user_id']} has successfully received a prize of {event.text} USDT.\n",
                reply_markup=HomeMenu.keyboard(),
                parse_mode='Markdown'
            )
            return await bot.send_message(
                chat_id=data['user_id'],
                text="🎉 *Congratulations!* \n"
                     "\n"
                     f"You are fortunate to have won a prize of {event.text} USDT.\n",
                parse_mode="Markdown"
            )

        await event.answer(
            text=response["message"],
            reply_markup=HomeMenu.keyboard()
        )

@handle_error
async def top_referrers(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.top_referrers.set()

    response = requests.get(
        url="http://127.0.0.1:8000/admin/top_referrers"
    ).json()["data"]

    text = ""
    for i, v in response.items():
        text += f"{v['telegram_id']} / {'@' + v['username'] if v['username'] else 'None'} / {v['reffered_friends']}\n"

    await event.message.answer(
        text="🏆 Top Referrers\n"
             "\n"
             "UserID / Username / Friends Referred\n"
             f"{text}",
        reply_markup=HomeMenu.keyboard(),
    )


@handle_error
async def accept_withdraw(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    withdrawal_id = event.data[:36]

    response = requests.post(
        url=f"http://127.0.0.1:8000/admin/approve_withdrawal?admin_id={event.from_user.id}&withdrawal_id={withdrawal_id}"
    ).json()

    if response["status"] == 200:
        text = event.message.text[25:]

        await event.message.edit_text(
            text=f"*✅ Withdrawal Request Approved*\n"
                 f"{text}",
            reply_markup={},
            parse_mode="Markdown"
        )

        await bot.send_message(
            chat_id=response["data"]["user_id"],
            text="✅ *Withdrawal Request Approved*\n"
                 "\n"
                 "Hello! Your withdrawal request has been successfully approved.\n"
                 "\n"
                 f"Requested Amount: {response['data']['amount']} USDT\n"
                 "The funds will be transferred to your account shortly.\n"
                 "\n"
                 "For further questions, please join our channel.\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )


@handle_error
async def decline_withdraw(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    withdrawal_id = event.data[:36]

    response = requests.post(
        url=f"http://127.0.0.1:8000/admin/decline_withdrawal?admin_id={event.from_user.id}&withdrawal_id={withdrawal_id}"
    ).json()

    if response["status"] == 200:
        text = event.message.text[25:]

        await event.message.edit_text(
            text=f"*❌ Withdrawal Request Declined*\n"
                 f"{text}",
            reply_markup={},
            parse_mode="Markdown"
        )

        await bot.send_message(
            chat_id=response["data"]["user_id"],
            text="❌ *Withdrawal Request Declined*\n"
                 "\n"
                 "Hello! We regret to inform you that your withdrawal request has been declined.\n"
                 "\n"
                 "Please make sure to submit a valid USDT-Ton address provided by Telegram Wallet when applying for a withdrawal.\n"
                 "\n"
                 "For further questions, please join our channel.\n",
            reply_markup=HomeMenu.keyboard(),
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
        accept_withdraw,
        Text(
            endswith=WithdrawMenu.accept_withdraw_callback
        )
    )
    dp.register_callback_query_handler(
        decline_withdraw,
        Text(
            endswith=WithdrawMenu.decline_withdraw_callback
        )
    )
    dp.register_callback_query_handler(
        top_referrers,
        Text(
            equals=AdminMenu.top_referrers_callback
        ),
        state=access_states
    )