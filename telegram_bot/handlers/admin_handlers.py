import csv
import requests

from aiogram import Dispatcher
from config import settings, bot, bot_settings
from utils import utils
from aiocryptopay import AioCryptoPay, Networks
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
    CashierMenu,
    PretzelsMenu,
    TopReferrersMenu,
    RetweetingTaskEditMenu,
    ManageGiftMenu,
    RallySettingsMenu,
    JoinRallyMenu
)


access_states = [
    AdminStates.admin_panel,
    AdminStates.overview,
    AdminStates.user_data,
    AdminStates.lucky_user,
    AdminStates.lucky_amount,
    AdminStates.weekly_referrers,
    AdminStates.top_referrers,
    AdminStates.main_wallet,
    AdminStates.change_wallet,
    AdminStates.cashier,
    AdminStates.invoice_amount,
    AdminStates.welcome_gift,
    AdminStates.retweeting_task,
    AdminStates.submit_link,
    AdminStates.rally_settings,
    AdminStates.select_round
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
    await event.answer(
        text="Refreshing..."
    )
    msg = await event.message.answer(
        text="📊 <b>Overview Loading...</b>\n"
             "\n"
             f"⏰ Total users: -\n"
             f"⏰ Total Registered Users: -\n"
             f"⏰ Today: -\n"
             "\n"
             f"⏰ Total Completed Tasks: -\n"
             f"⏰ Total Referrals: -\n"
             f"\n"
             f"⏰ Total Pretzels: -\n"
             f"⏰ Redeemed: -\n"
             f"⏰ Total Gifted: -",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )
    response = requests.get(f"{settings.BASE_API_URL}/admin/overview").json()["data"]
    await msg.edit_text(
        text="📊 <b>Overview</b>\n"
             "\n"
             f"👥 Total users: {response['total_users']}\n"
             f"👥 Total Registered Users: {response['registered_users']}\n"
             f"👥 Today: {response['registered_today']}\n"
             "\n"
             f"✅ Total Completed Tasks: {response['total_completed_tasks']}\n"
             f"✅ Total Referrals: {response['total_refferals']}\n"
             f"\n"
             f"🥨 Total Pretzels: {response['total_pretzels']}\n"
             f"🥨 Redeemed: {response['redeemed_pretzels']}\n"
             f"🥨 Total Gifted: {response['gifted_pretzels']}",
        reply_markup=AdminMenu.admin_menu(),
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


@handle_error
async def user_data(
        event: Message,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.text}"
    )

    if response.status_code == 200:

        response_data = response.json()["data"]

        current_withdrawal = requests.post(
            url=f"{settings.BASE_API_URL}/user/current_withdrawal",
            json={
                "withdrawal_id": response_data['current_withdrawal']
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
                 f"<b>UserID</b>: {response_data['telegram_id']}\n"
                 f"<b>Username</b>: {'@' + response_data['username'] if response_data['username'] else 'None'}\n"
                 f"<b>Completed Tasks</b>: {completed_tasks['total_completed']} / {completed_tasks['completed_today']}\n"
                 f"<b>Friends Referred</b>: {len(response_data['referred_friends'])}\n"
                 f"<b>Current Balance</b>: {response_data['balance']} USDT\n"
                 f"<b>Withdrawal Request</b>: {current_withdrawal['data']['amount'] if current_withdrawal['status'] == 200 else 0} USDT\n"
                 f"<b>Total Withdrawals</b>: {total_withdrawals['total_withdrawals']} USDT\n"
                 f"<b>Pretzel</b>: {response_data['pretzels']['balance']} / {response_data['pretzels']['redeemed']}",
            reply_markup=AdminMenu.resend_keyboard(
                user_id=response_data['telegram_id']
            ),
            parse_mode="HTML"
        )

    await event.answer(
        text=response["message"],
        reply_markup=AdminMenu.admin_menu()
    )


@handle_error
async def resend_withdrawal(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    user_id = event.data[:-13]
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{user_id}"
    )
    response_data = response.json()["data"]
    current_withdrawal = requests.post(
        url=f"{settings.BASE_API_URL}/user/current_withdrawal",
        json={
            "withdrawal_id": response_data['current_withdrawal']
        }
    )

    if current_withdrawal.status_code == 200:
        withdrawal_response = current_withdrawal.json()["data"]

        await bot.send_message(
            chat_id=settings.ADMINS_CHAT,
            text="🆕 <b>New Withdrawal Request</b>\n"
                 "\n"
                 f"<b>User ID</b>: {user_id}\n"
                 f"<b>Username</b>: {'@' + response_data['username']}\n"
                 f"<b>Requested Balance</b>: {withdrawal_response['amount']} USDT\n",
            reply_markup=WithdrawMenu.control(
                withdrawal_id=response_data['current_withdrawal']
            ),
            parse_mode="HTML"
        )
        return await event.answer(
            text="📪 Withdrawal request has been resent.",
            show_alert=True
        )

    await event.answer(
        text="📭 The user has no pending withdrawal requests.",
        show_alert=True
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
            reply_markup=AdminMenu.admin_menu()
        )


@handle_error
async def choose_rank(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="Choose a Rank:",
        reply_markup=TopReferrersMenu.keyboard()
    )


@handle_error
async def weekly_referrers(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.weekly_referrers.set()
    await event.answer(
        text="⏱️ Loading may take up to 30 seconds!",
        cache_time=5
    )
    await event.message.edit_text(
        text="⏰ <b>Weekly Top Referrers Loading...</b>",
        parse_mode="HTML"
    )

    response = requests.get(
        url=f"{settings.BASE_API_URL}/admin/top_referrers"
    ).json()["data"]

    text = ""
    for i, v in response["weekly_top"].items():
        text += f"{i.zfill(2)} / {v['telegram_id']} / {v['reffered_friends']}{f' / 👟' if v['on_rally'] else ''}\n"

    await event.message.edit_text(
        text="🏆 <b>Weekly Top Referrers</b>\n"
             "\n"
             "<b>Ranking / UserID / Friends Referred</b>\n"
             f"{text}",
        reply_markup=AdminMenu.admin_menu(),
        parse_mode="HTML"
    )


@handle_error
async def top_referrers(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.top_referrers.set()
    await event.answer(
        text="⏱️ Loading may take up to 30 seconds!",
        cache_time=5
    )
    await event.message.edit_text(
        text="⏰ <b>Top Referrers Loading...</b>",
        parse_mode="HTML"
    )

    response = requests.get(
        url=f"{settings.BASE_API_URL}/admin/top_referrers"
    ).json()["data"]

    text = ""
    for i, v in response["top_referrers"].items():
        text += f"{v['telegram_id']} / {'@' + v['username'] if v['username'] else 'None'} / {v['reffered_friends']}\n"

    await event.message.edit_text(
        text="🏆 <b>Top Referrers</b>\n"
             "\n"
             "<b>UserID / Username / Friends Referred</b>\n"
             f"{text}",
        reply_markup=AdminMenu.admin_menu(),
        parse_mode="HTML"
    )


@handle_error
async def welcome_gift(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.welcome_gift.set()
    await event.message.answer(
        text="Select the task you want to edit:",
        reply_markup=ManageGiftMenu.keyboard()
    )


@handle_error
async def retweeting_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.retweeting_task.set()
    await event.message.answer(
        text="Select the one of settings you want to change:",
        reply_markup=RetweetingTaskEditMenu.keyboard()
    )


@handle_error
async def retweeting_link(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.submit_link.set()
    await event.message.answer(
        text=f"Currect link - {bot_settings.RETWEETING_LINK}\n"
             "\n"
             "Submit the link:",
        reply_markup=AdminMenu.admin_menu(),
        disable_web_page_preview=True
    )


@handle_error
async def set_link(
        event: Message,
        state: FSMContext
) -> None:
    if event.text[:14] != "https://x.com/":
        return await event.answer(
            text="<i>Invalid link, please submit again.</i>",
            reply_markup=AdminMenu.admin_menu(),
            parse_mode="HTML"
        )
    utils.update_settings(
        {
            "RETWEETING_LINK": event.text
        }
    )
    await event.answer(
        text="✅ The new link is set.",
        reply_markup=AdminMenu.admin_menu()
    )
    await AdminStates.welcome_gift.set()


@handle_error
async def rally_settings(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    if event.from_user.id != 1125858430:
        return await event.answer(
            text="🚧 Currently Unavailable.",
            show_alert=True
        )

    await AdminStates.rally_settings.set()
    response = requests.get(
        url=f"{settings.BASE_API_URL}/rally"
    )
    response_data = response.json()["data"]

    await event.message.answer(
        text=f"🏎️ <b>Rally Settings</b>\n"
             f"\n"
             f"🏁 <b>Round</b>: {response_data['active']['round']}\n"
             f"🕒 <b>Start time</b>: {utils.from_timestamp(response_data['active']['start_time'])}\n"
             f"🕒 <b>End time</b>: {utils.from_timestamp(response_data['active']['end_time'])}",
        reply_markup=RallySettingsMenu.keyboard(),
        parse_mode="HTML"
    )


@handle_error
async def new_rally(
        event: CallbackQuery,
        state: FSMContext
) -> None:

    pass


@handle_error
async def choose_round(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.select_round.set()
    await event.message.answer(
        text="Select round: "
    )

@handle_error
async def send_invitations(
        event: Message,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/rally/{event.text}"
    )
    response_data = response.json()["data"]

    if response.status_code == 200:
        if not response_data["allowed_users"]:
            return await event.answer(
                text="Not support rallys without allowed users."
            )

        msg = await event.answer(
            text=f"Round {event.text} with allowed users: {[f'{i}, ' for i in response_data['allowed_users']]} sending invitations..."
        )

        for i in response_data["allowed_users"]:
            try:
                await bot.send_message(
                    chat_id=i,
                    text=f"Are you ready for <b>Round {event.text}</b> of the <b>Top Referrals Rally</b>?\n"
                         f"\n"
                         f"🕒 <b>Start time</b>: {utils.from_timestamp(response_data['start_time'])}\n"
                         f"🕒 <b>End time</b>: {utils.from_timestamp(response_data['end_time'])}\n"
                         f"\n"
                         f"<i>Click the button below to sign up</i> 👇👇",
                    reply_markup=JoinRallyMenu.keyboard(
                        user_id=i,
                        round=event.text
                    ),
                    parse_mode="HTML"
                )
                status = "✅"
            except:
                status = "❌"

            await event.answer(
                text=f"{i}: {status}"
            )

        return await event.answer(
            text=f"Invitations sent."
        )

    return await event.answer(
        text=f"Error."
    )



@handle_error
async def cashier(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.cashier.set()

    balance = None
    crypto_bot = AioCryptoPay(
        token=settings.CRYPTOBOT_TOKEN,
        network=Networks.MAIN_NET
    )

    try:
        balance = f"{(await crypto_bot.get_balance())[0].available} USDT"
    except:
        pass

    msg = await event.message.answer(
        text="🏧 <b>Cashier Loading...</b>\n"
             "\n"
             f"⏰ Total Transfer: -\n"
             f"⏰ This Month: -\n"
             f"⏰ This Week: -\n"
             f"\n"
             f"💰 Balance: {balance}",
        reply_markup=CashierMenu.keyboard(),
        parse_mode="HTML"
    )

    response = requests.get(
        url=f"{settings.BASE_API_URL}/admin/cashier_statistics"
    ).json()["data"]

    await msg.edit_text(
        text="🏧 <b>Cashier</b>\n"
             "\n"
             f"💸 Total Transfer: {response['total_transfer']:.1f} USDT\n"
             f"💸 This Month: {response['this_month']:.1f} USDT\n"
             f"💸 This Week: {response['this_week']:.1f} USDT\n"
             f"\n"
             f"💰 Balance: {balance}",
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
async def invoice_amount(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await AdminStates.invoice_amount.set()
    await event.message.answer(
        text="<i>Enter amount of the invoice:</i>",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )


@handle_error
async def deposit_balance(
        event: Message,
        state: FSMContext
) -> None:
    crypto_bot = AioCryptoPay(
        token=settings.CRYPTOBOT_TOKEN,
        network=Networks.MAIN_NET
    )

    try:
        amount = float(
            event.text
        )
        invoice = await crypto_bot.create_invoice(
            amount=amount,
            asset="USDT"
        )
    except:
        return await event.answer(
            text="<i>Invalid amount.</i>",
            parse_mode="HTML"
        )

    await event.answer(
        text="<i>To deposit the balance, pay the invoice:</i>",
        reply_markup=AdminMenu.pay_button(
            amount=amount,
            invoice_url=invoice.bot_invoice_url
        ),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=1125858430,
        text=f"New deposit for {amount:.1f} USDT"
    )


@handle_error
async def weekly_report(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/admin/weekly_report"
    ).json()["data"]

    rows = response["rows"]
    rows.insert(
        0, response["values"]
    )

    with open("images/report.csv", mode='w', newline='') as file:
        writer = csv.writer(
            file
        )
        writer.writerows(rows)

    await event.message.reply_document(
        document=open(
            "images/report.csv",
            "rb"
        ),
        caption="📑 <i>Weekly Report:</i>",
        reply_markup=AdminMenu.admin_menu(),
        parse_mode="HTML"
    )


@handle_error
async def accept_withdraw(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    withdrawal_id = event.data[:36]

    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/approve_withdrawal?admin_id={event.from_user.id}&withdrawal_id={withdrawal_id}&message_id={event.message.message_id}"
    )

    if response.status_code == 200:
        response_data = response.json()["data"]
        text = event.message.text[25:]

        await event.message.edit_text(
            text=f"<b>⏰ Withdrawal Request in Progress</b>\n"
                 f"{text}",
            reply_markup={},
            parse_mode="HTML"
        )

        transfer_response = requests.post(
            url=f"{settings.BASE_API_URL}/user/{response_data['user_id']}/transfer_funds",
            json={
                "token": settings.CRYPTOBOT_TOKEN
            }
        )

        if transfer_response.status_code == 200:

            transfer_data = transfer_response.json()["data"]
            withdrawal_data = transfer_data["request"]

            if transfer_data["status"] == "sent":
                try:
                    await event.message.edit_text(
                        text="✅ <b>Withdrawal Request Approved</b>\n"
                             "\n"
                             f"<b>User ID</b>: {withdrawal_data['user_id']}\n"
                             f"<b>Username</b>: {withdrawal_data['username']}\n"
                             f"<b>Requested Balance</b>: {withdrawal_data['amount']} USDT\n"
                             f"\n"
                             f"<b>Payment status</b>: Sent\n"
                             f"<b>Last activity</b>: {transfer_data['updated_at']}",
                        reply_markup={},
                        parse_mode="HTML"
                    )
                    await bot.send_message(
                        chat_id=withdrawal_data["user_id"],
                        text="✅ <b>Withdrawal Request Approved</b>\n"
                             "\n"
                             "Hello! Your withdrawal request has been successfully approved.\n"
                             "\n"
                             f"<b>Requested Amount</b>: {withdrawal_data['amount']} USDT\n"
                             "The funds will be transferred to your account shortly.\n"
                             "\n"
                             "For further questions, please join our channel.\n",
                        reply_markup=HomeMenu.keyboard(),
                        parse_mode="HTML"
                    )
                except:
                    pass

            elif transfer_data["status"] == "failed":

                requests.post(
                    url=f"{settings.BASE_API_URL}/admin/reset_withdrawal?withdrawal_id={withdrawal_data['id']}"
                )

                try:
                    await event.message.edit_text(
                        text="🆕 <b>New Withdrawal Request</b>\n"
                             "\n"
                             f"<b>User ID</b>: {withdrawal_data['user_id']}\n"
                             f"<b>Username</b>: {withdrawal_data['username']}\n"
                             f"<b>Requested Balance</b>: {withdrawal_data['amount']} USDT\n"
                             f"\n"
                             f"<b>Payment status</b>: Failed\n"
                             f"<b>Last activity</b>: {transfer_data['updated_at']}",
                        reply_markup=WithdrawMenu.control(
                            withdrawal_id=withdrawal_data["id"]
                        ),
                        parse_mode="HTML"
                    )
                except:
                    pass


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
                 "Please make sure you’ve activated your wallet in <a href='https://t.me/send'>Crypto Bot</a>.\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )


@handle_error
async def accept_pretzel_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    task_id = event.data[:36]

    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/approve_pretzel_task?admin_id={event.from_user.id}&task_id={task_id}"
    ).json()

    if response["status"] == 200:
        response_data = response["data"]

        await event.message.edit_text(
            text=f"✅ <b>Pretzel Order Approved</b>\n"
                 f"\n"
                 f"<b>User ID</b>: {response_data['user_id']}\n"
                 f"<b>Username</b>: {response_data['username']}\n"
                 f"<b>Task</b>: {response_data['task']}\n"
                 f"<b>Submitted Info</b>: {response_data['payload']}\n",
            reply_markup={},
            parse_mode="HTML"
        )

        await bot.send_message(
            chat_id=response_data["user_id"],
            text=f"🎉 <b>Congratulations!</b> \n"
                 f"\n"
                 f"You received a reward of <b>{response_data['reward']} Pretzel{'s' if response_data['reward'] > 1 else ''}</b>\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )


@handle_error
async def decline_pretzel_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    task_id = event.data[:36]

    response = requests.post(
        url=f"{settings.BASE_API_URL}/admin/decline_pretzel_task?admin_id={event.from_user.id}&task_id={task_id}"
    ).json()

    if response["status"] == 200:
        response_data = response["data"]

        await event.message.edit_text(
            text=f"❌ <b>Pretzel Order Declined</b>\n"
                 f"\n"
                 f"<b>User ID</b>: {response_data['user_id']}\n"
                 f"<b>Username</b>: {response_data['username']}\n"
                 f"<b>Task</b>: {response_data['task']}\n"
                 f"<b>Submitted Info</b>: {response_data['payload']}\n",
            reply_markup={},
            parse_mode="HTML"
        )

        text = (
            "❌ <b>Pretzel Order Declined</b>\n"
            "\n"
            "Your submitted information does not meet the criteria. Please try again.\n"
        )

        if response_data["type"] in ["retweet_post"]:

            text = ("⛔️ <b>You missed the free Pretzel</b>\n"
                    "\n"
                    "Your submitted information does not meet the criteria.")

        await bot.send_message(
            chat_id=response_data["user_id"],
            text=text,
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
        resend_withdrawal,
        Text(
            endswith="_admin_resend"
        ),
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
        accept_pretzel_task,
        Text(
            endswith=PretzelsMenu.accept_pretzels_callback
        )
    )
    dp.register_callback_query_handler(
        decline_pretzel_task,
        Text(
            endswith=PretzelsMenu.decline_pretzels_callback
        )
    )
    dp.register_callback_query_handler(
        choose_rank,
        Text(
            equals=AdminMenu.top_referrers_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        weekly_referrers,
        Text(
            equals=TopReferrersMenu.weekly_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        top_referrers,
        Text(
            equals=TopReferrersMenu.all_time_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        welcome_gift,
        Text(
            equals=AdminMenu.welcome_gift_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        retweeting_task,
        Text(
            equals=ManageGiftMenu.retweeting_task_callback
        ),
        state=AdminStates.welcome_gift
    )
    dp.register_callback_query_handler(
        retweeting_link,
        Text(
            equals=RetweetingTaskEditMenu.url_button_callback
        ),
        state=AdminStates.retweeting_task
    )
    dp.register_message_handler(
        set_link,
        state=AdminStates.submit_link
    )
    dp.register_callback_query_handler(
        rally_settings,
        Text(
            equals=AdminMenu.rally_settings_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        new_rally,
        Text(
            equals=RallySettingsMenu.new_rally_callback
        ),
        state=access_states
    )
    dp.register_callback_query_handler(
        choose_round,
        Text(
            equals=RallySettingsMenu.send_invitations_callback
        ),
        state=access_states
    )
    dp.register_message_handler(
        send_invitations,
        state=AdminStates.select_round
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
    dp.register_callback_query_handler(
        invoice_amount,
        Text(
            equals=CashierMenu.deposit_callback
        ),
        state=AdminStates.cashier
    )
    dp.register_message_handler(
        deposit_balance,
        state=AdminStates.invoice_amount
    )
    dp.register_callback_query_handler(
        weekly_report,
        Text(
            equals=CashierMenu.weekly_report_callback
        ),
        state=AdminStates.cashier
    )