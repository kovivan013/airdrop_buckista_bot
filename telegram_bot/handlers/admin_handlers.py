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
    WithdrawMenu,
    CashierMenu
)


access_states = [
    AdminStates.admin_panel,
    AdminStates.overview,
    AdminStates.user_data,
    AdminStates.lucky_user,
    AdminStates.lucky_amount,
    AdminStates.top_referrers,
    AdminStates.main_wallet,
    AdminStates.change_wallet,
    AdminStates.cashier
]

@handle_error
async def check_admin(
        event: Message,
        state: FSMContext
) -> None:
    await AdminStates.enter_password.set()
    await event.answer(
        text="<i>Enter admin password:</i>",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
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
            text="<i>Incorrect password, please try again.<i>",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )
    await AdminStates.admin_panel.set()
    await event.answer(
        text="<i>You have successfully logged in as an administrator.</i>",
        reply_markup=AdminMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def admin_message(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.admin_panel.set()
    await event.message.answer(
        text="<i>You have successfully logged in as an administrator.</i>",
        reply_markup=AdminMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def overview(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.overview.set()
    response = requests.get(f"{settings.BASE_API_URL}/admin/overview").json()["data"]
    await event.message.answer(
        text="📊 <b>Overview</b>\n"
             "\n"
             f"👥 Total users: {response['total_users']}\n"
             f"👥 Total Registered Users: {response['registered_users']}\n"
             f"👥 Today: {response['registered_today']}\n"
             "\n"
             f"✅ Total Completed Tasks: {response['total_completed_tasks']}\n"
             f"✅ Total Referrals: {response['total_refferals']}\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def enter_user_id(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.user_data.set()
    await event.message.answer(
        text="📊 *User Data*\n"
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
        url=f"{settings.BASE_API_URL}/user/{event.text}"
    ).json()

    if response["status"] == 200:
        current_withdrawal = requests.post(
            url=f"{settings.BASE_API_URL}/user/current_withdrawal",
            json={
                "withdrawal_id": response['data']['current_withdrawal']
            }
        ).json()
        total_withdrawals = requests.get(
            url=f"{settings.BASE_API_URL}/user/{event.text}/total_withdrawals"
        ).json()["data"]
        completed_tasks = requests.get(
            url=f"{settings.BASE_API_URL}/user/{event.text}/completed_tasks"
        ).json()["data"]
        return await event.answer(
            text="📊 <b>User Data</b>\n"
                 "\n"
                 f"<b>UserID</b>: {response['data']['telegram_id']}\n"
                 f"<b>Username</b>: {'@' + response['data']['username'] if response['data']['username'] else 'None'}\n"
                 f"<b>Completed Tasks</b>: {completed_tasks['total_completed']} / {completed_tasks['completed_today']}\n"
                 f"<b>Friends Referred</b>: {len(response['data']['referred_friends'])}\n"
                 f"<b>Current Balance</b>: {response['data']['balance']} USDT\n"
                 f"<b>Withdrawal Request</b>: {current_withdrawal['data']['amount'] if current_withdrawal['status'] == 200 else 0} USDT\n"
                 f"<b>Total Withdrawals</b>: {total_withdrawals['total_withdrawals']} USDT",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
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
        text="🎰 *Lucky Draw*\n"
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
        text="🎰 *Lucky Draw*\n"
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
            url=f"{settings.BASE_API_URL}/user/{data['user_id']}/increase_balance?amount={event.text}"
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
                     f"You are fortunate to have won a prize of *{event.text} USDT*.\n",
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
        url=f"{settings.BASE_API_URL}/admin/top_referrers"
    ).json()["data"]

    text = ""
    for i, v in response.items():
        text += f"{v['telegram_id']} / {'@' + v['username'] if v['username'] else 'None'} / {v['reffered_friends']}\n"

    await event.message.answer(
        text="🏆 <b>Top Referrers</b>\n"
             "\n"
             "<b>UserID / Username / Friends Referred</b>\n"
             f"{text}",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def cashier(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.cashier.set()
    await event.message.answer(
        text="🏧 <b>Cashier</b>\n"
             "\n"
             f"💸 Total Transfer: 1276.4 USDT\n"
             f"💸 This Month: 375.2 USDT\n"
             f"💸 This Week: 34 USDT\n"
             f"\n"
             f"📩 <u>Download the weekly report in CSV</u>",
        reply_markup=CashierMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def main_wallet(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.main_wallet.set()
    await event.message.answer(
        text=f"🗝️ <b>Main Wallet</b>\n"
             f"\n"
             f"{settings.CRYPTOBOT_TOKEN}",
        reply_markup=CashierMenu.change_keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def change_wallet(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.change_wallet.set()
    await event.message.answer(
        text=f"🗝️ <b>Change Wallet</b>\n"
             f"\n"
             f"Submit a new CryptoBot token",
        reply_markup=AdminMenu.admin_menu(),
        parse_mode="HTML"
    )

@handle_error
async def set_wallet(
        event: Message,
        state: FSMContext
) -> None:
    settings.CRYPTOBOT_TOKEN = event.text
    await event.answer(
        text=f"✅ The main wallet has been successfully replaced",
        reply_markup=CashierMenu.replaced_keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def accept_withdraw(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    print(event.message, event.message.message_id)
    withdrawal_id = event.data[:36]

    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/approve_withdrawal?admin_id={event.from_user.id}&withdrawal_id={withdrawal_id}&message_id={event.message.message_id}"
    ).json()

    if response["status"] == 200:
        text = event.message.text[25:]

        await event.message.edit_text(
            text=f"<b>⏰ Withdrawal Request in Progress</b>\n"
                 f"{text}",
            reply_markup={},
            parse_mode="HTML"
        )

        # await bot.send_message(
        #     chat_id=response["data"]["user_id"],
        #     text="✅ <b>Withdrawal Request Approved</b>\n"
        #          "\n"
        #          "Hello! Your withdrawal request has been successfully approved.\n"
        #          "\n"
        #          f"<b>Requested Amount</b>: {response['data']['amount']} USDT\n"
        #          "The funds will be transferred to your account shortly.\n"
        #          "\n"
        #          "For further questions, please join our channel.\n",
        #     reply_markup=HomeMenu.keyboard(),
        #     parse_mode="HTML"
        # )


@handle_error
async def decline_withdraw(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    withdrawal_id = event.data[:36]

    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/decline_withdrawal?admin_id={event.from_user.id}&withdrawal_id={withdrawal_id}&message_id={event.message.message_id}"
    ).json()

    if response["status"] == 200:
        text = event.message.text[25:]

        await event.message.edit_text(
            text=f"❌ <b>Withdrawal Request Declined</b>\n"
                 f"{text}",
            reply_markup={},
            parse_mode="HTML"
        )

        await bot.send_message(
            chat_id=response["data"]["user_id"],
            text="❌ <b>Withdrawal Request Declined</b>\n"
                 "\n"
                 "Hello! We regret to inform you that your withdrawal request has been declined.\n"
                 "\n"
                 "Please make sure to submit a valid <b>USDT-Ton</b> address provided by <b>Telegram Wallet</b> when applying for a withdrawal.\n"
                 "\n"
                 "For further questions, please join our channel.\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
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
    dp.register_callback_query_handler(
        cashier,
        Text(
            equals=AdminMenu.cashier_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        main_wallet,
        Text(
            equals=CashierMenu.main_wallet_callback
        ),
        state=[
            AdminStates.cashier,
            AdminStates.change_wallet
        ]
    )
    dp.register_callback_query_handler(
        change_wallet,
        Text(
            equals=CashierMenu.change_wallet_callback
        ),
        state=AdminStates.main_wallet
    )
    dp.register_message_handler(
        set_wallet,
        state=AdminStates.change_wallet
    )
    dp.register_callback_query_handler(
        admin_message,
        Text(
            equals=AdminMenu.admin_callback
        ),
        state=access_states
    )