import requests
from aiogram import Dispatcher
import aiohttp
from config import bot, settings
from aiogram.types import (
    Message,
    CallbackQuery,
    InputFile
)
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from states.states import (
    ReferralStates
)
from decorators.decorators import private_message, handle_error
from keyboards.keyboards import (
    DescriptionMenu,
    TasksListMenu,
    WebAppTasksMenu,
    AndroidAppTasksMenu,
    IOSAppTasksMenu,
    InviteMenu,
    WithdrawMenu,
    HomeMenu
)
from common.schemas import (
    BaseReferral,
    ResponseMessages
)

@handle_error
async def home(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await state.finish()
    await event.message.answer(
        text=f"🎉 Hello {event.from_user.username}! \n"
             "==============================\n"
             "\n"
             "🚨 Join the *BioMatrix Airdrop* to earn more rewards:\n"
             "\n"
             "🔹 *Task Reward*\n"
             "🔸 Unlimited Prize Pool\n"
             "🔸 0.3 USDT + 100 POY for using APP\n"
             "🔸 0.4 USDT for each valid invitation\n"
             "\n"
             "🔹 *Lucky Draw*\n"
             "🔸 2500 USDT Summer Giveaway\n"
             "🔸 500 participants will be randomly rewarded\n"
             "\n"
             "🔹 *Referral Reward*\n"
             "🔸 The top 30 referrers share 2500 USDT\n"
             "🔸 1st place: 1000 USDT\n"
             "🔸 2nd place: 500 USDT\n"
             "🔸 3rd place: 250 USDT\n"
             "🔸 4th place: 100 USDT\n"
             "🔸 5th to 30th place: 50 USDT each\n"
             "\n"
             "📅 *End Date*: 30 September 2024\n"
             "🚀 *Distribution Time*: Up to 7 working days\n"
             "\n"
             "==============================\n"
             "⬇️ **Click BioMatrix Airdrop and explore the tasks available**\n"
             "⬇️ **Click My Balance to withdraw your rewards at any time**",
        reply_markup=DescriptionMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def start(
        event: Message,
        state: FSMContext
) -> None:
    try:
        referrer_id = int(
            event.text.split()[1]
        )
        response = requests.post(
            url=f"http://127.0.0.1:8000/user/{event.from_user.id}/refer_friend?referrer_id={referrer_id}"
        )
        if response.json()["status"] != 200:
            await event.answer(
                text=response.json()["message"]
            )
        else:
            await bot.send_message(
                chat_id=referrer_id,
                text="🎉 New Referral Registered! 🎉\n"
                     "\n"
                     "👤 A new user has registered using your referral link.\n"
                     "\n"
                     "💸 You received a reward of 0.4 USDT\n"
            )
            requests.put(
                url=f"http://127.0.0.1:8000/user/{referrer_id}/increase_balance?amount=0.4"
            )
    except:
        pass
    requests.post(
        url="http://127.0.0.1:8000/user/create_user",
        json={
            "telegram_id": event.from_user.id,
            "username": event.from_user.username if event.from_user.username else ""
        }
    )
    await event.answer(
        text=f"🎉 Hello {event.from_user.username}! \n"
             "==============================\n"
             "\n"
             "🚨 Join the *BioMatrix Airdrop* to earn more rewards:\n"
             "\n"
             "🔹 *Task Reward*\n"
             "🔸 Unlimited Prize Pool\n"
             "🔸 0.3 USDT + 100 POY for using APP\n"
             "🔸 0.4 USDT for each valid invitation\n"
             "\n"
             "🔹 *Lucky Draw*\n"
             "🔸 2500 USDT Summer Giveaway\n"
             "🔸 500 participants will be randomly rewarded\n"
             "\n"
             "🔹 *Referral Reward*\n"
             "🔸 The top 30 referrers share 2500 USDT\n"
             "🔸 1st place: 1000 USDT\n"
             "🔸 2nd place: 500 USDT\n"
             "🔸 3rd place: 250 USDT\n"
             "🔸 4th place: 100 USDT\n"
             "🔸 5th to 30th place: 50 USDT each\n"
             "\n"
             "📅 *End Date*: 30 September 2024\n"
             "🚀 *Distribution Time*: Up to 7 working days\n"
             "\n"
             "==============================\n"
             "⬇️ **Click BioMatrix Airdrop and explore the tasks available**\n"
             "⬇️ **Click My Balance to withdraw your rewards at any time**",
        reply_markup=DescriptionMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def tasks_list(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="🎯 **Complete Tasks & Earn Rewards!**\n"
             "\n"
             "💎 Get **0.3 USDT** for using our Web APP\n"
             "💎 Get **0.3 USDT** for using our iOS APP\n"
             "💎 Get **0.3 USDT** for using our Android APP\n"
             "💎 Get **0.4 USDT** for each valid invitation",
        reply_markup=TasksListMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def user_balance(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"http://127.0.0.1:8000/user/{event.from_user.id}"
    ).json()["data"]
    current_withdrawal = requests.get(
        url=f"http://127.0.0.1:8000/user/current_withdrawal?withdrawal_id={response['current_withdrawal']}"
    ).json()
    total_withdrawals = requests.get(
        url=f"http://127.0.0.1:8000/user/{event.from_user.id}/total_withdrawals"
    ).json()["data"]
    await event.message.answer(
        text=f"💰 Your Current Balance: {response['balance']} USDT\n"
             "\n"
             f"➡️ Withdrawal Request: {current_withdrawal['data']['amount'] if current_withdrawal['status'] == 200 else 0} USDT\n"
             f"🤑 Total Withdrawals: {total_withdrawals['total_withdrawals']} USDT\n"
             "\n"
             f"👥 Friends Referred: {len(response['referred_friends'])}\n"
             "\n"
             "**Please note that your withdrawal requires the Telegram Wallet to be activated**"
        ,
        reply_markup=WithdrawMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def submit_referral(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await ReferralStates.submit_referral.set()
    await event.message.answer(

        text="✅ Click Settings\n"
             "✅ Scroll To The Referral Code Section\n"
             "✅ Copy your Referral Code\n"
             "\n"
             "Then submit your Referral Code:\n",
        parse_mode="Markdown"
    )

@handle_error
async def check_referral(
        event: Message,
        state: FSMContext
) -> None:
    await ReferralStates.checked_code.set()
    response = BaseReferral().model_validate(
        requests.get(
            f"https://rds-service.bio-matrix.com/redeemReferCode/{event.text}"
        ).json()
    )

    if response.Succ:
        if response.refer_code_status == ResponseMessages.valid_code:
            return await event.answer(
                text="🎉 Your referral code is valid! Your balance has been increased by 0.3 USDT.",
                reply_markup=HomeMenu.keyboard(),
                parse_mode="Markdown"
            )
        elif response.refer_code_status == ResponseMessages.already_redeemed:
            return await event.answer(
                text="⚠️ This referral code has already been used. Please check and try again.",
                reply_markup=HomeMenu.keyboard(),
                parse_mode="Markdown"
            )

    await event.answer(
        text="❗️ Your referral code is invalid! Check the number of written characters and try again.",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )


@handle_error
async def web_app_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 Use BioMatrix Web App\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ Register on the Web APP\n"
             "2️⃣ Copy the Referral Code from the APP\n"
             "3️⃣ Submit your Referral Code\n"
             "\n"
             "💰 You will earn 0.3 USDT and 100 POY for completing this task",
        reply_markup=WebAppTasksMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def android_app_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 Use BioMatrix Android App\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ Register on the Android APP\n"
             "2️⃣ Copy the Referral Code from the APP\n"
             "3️⃣ Submit your Referral Code\n"
             "\n"
             "💰 You will earn 0.3 USDT and 100 POY for completing this task",
        reply_markup=AndroidAppTasksMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def ios_app_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 Use BioMatrix iOS App\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ Register on the iOS APP\n"
             "2️⃣ Copy the Referral Code from the APP\n"
             "3️⃣ Submit your Referral Code\n"
             "\n"
             "💰 You will earn 0.3 USDT and 100 POY for completing this task",
        reply_markup=IOSAppTasksMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def enter_ton_address(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await ReferralStates.withdraw_address.set()
    response = requests.get(
        url=f"http://127.0.0.1:8000/user/{event.from_user.id}"
    ).json()["data"]

    if float(response["balance"]) > 1:
        current_withdrawal = requests.get(
            url=f"http://127.0.0.1:8000/user/current_withdrawal?withdrawal_id={response['current_withdrawal']}"
        ).json()
        if current_withdrawal["status"] == 200 and current_withdrawal["data"]["status"] in ["approved", "declined"]:
            return await event.message.answer(
                text="❌ You cannot submit a new withdrawal request until your latest one has been processed. Thank you for your patience.",
                reply_markup=HomeMenu.keyboard(),
                parse_mode="Markdown"
            )
        return await event.message.answer(
            text=f"💵 Withdrawal Amount: {response['balance']} USDT\n"
                 "\n"
                 "We only accept USDT-TON address from your Telegram Wallet\n"
                 "\n"
                 "Submit your USDT-TON Address\n",
            reply_markup=HomeMenu.keyboard()
        )

    await event.message.answer(
        text="❌ *Minimum withdrawal amount 1 USDT*",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def withdraw_balance(
        event: Message,
        state: FSMContext
) -> None:
    withdrawal = requests.post(
        url=f"http://127.0.0.1:8000/user/{event.from_user.id}/withdraw",
        json={
            "ton_address": event.text
        }
    ).json()["data"]
    await event.answer(
        text="✅ *Withdrawal Request Submitted*\n"
             "\n"
             "Your withdrawal request has been successfully submitted. 🎉\n"
             "We will review and process it within *7 business days*. Thank you for your patience! 😊\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )
    await bot.send_message(
        chat_id=settings.ADMINS_CHAT,
        text="🆕 New Withdrawal Request\n"
             "\n"
             f"User ID: {event.from_user.id}\n"
             f"Username: {'@' + event.from_user.username if event.from_user.username else 'None'}\n"
             f"TON Wallet Address: {event.text}\n"
             f"Requested Balance: {withdrawal['amount']} USDT\n",
        reply_markup=WithdrawMenu.control(
            withdrawal_id=withdrawal["id"]
        ),
        parse_mode="Markdown"
    )

@handle_error
async def invite_friend(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"http://127.0.0.1:8000/user/{event.from_user.id}"
    ).json()["data"]
    await event.message.answer(
        text="🎉 Invite your friends to join our bot and earn rewards! When your friends claim the airdrop, you will receive a reward of 0.4 USDT.\n"
             "\n"
             f"🔗 Your Referral Link: https://t.me/officialBioMatrix_bot?start={event.from_user.id}\n"
             f"👥 Friends Referred: {len(response['referred_friends'])}\n"
             "\n"
             "Share this link with your friends and watch your balance grow! 🚀\n",
        reply_markup=InviteMenu.keyboard(
            user_id=event.from_user.id
        )
    )


def register(
        dp: Dispatcher
):
    dp.register_message_handler(
        start,
        commands=["start"]
    )
    dp.register_callback_query_handler(
        home,
        Text(
            equals=HomeMenu.home_callback
        ),
        state=["*"]
    )
    dp.register_callback_query_handler(
        tasks_list,
        Text(
            equals=DescriptionMenu.airdrop_callback
        )
    )
    dp.register_callback_query_handler(
        user_balance,
        Text(
            equals=DescriptionMenu.balance_callback
        )
    )
    dp.register_callback_query_handler(
        submit_referral,
        Text(
            equals=TasksListMenu.check_referral_callback
        )
    )
    dp.register_message_handler(
        check_referral,
        state=ReferralStates.submit_referral
    )
    dp.register_callback_query_handler(
        enter_ton_address,
        Text(
            WithdrawMenu.withdraw_callback
        )
    )
    dp.register_message_handler(
        withdraw_balance,
        state=ReferralStates.withdraw_address
    )
    dp.register_callback_query_handler(
        web_app_task,
        Text(
            equals=TasksListMenu.web_app_callback
        )
    )
    dp.register_callback_query_handler(
        android_app_task,
        Text(
            equals=TasksListMenu.android_app_callback
        )
    )
    dp.register_callback_query_handler(
        invite_friend,
        Text(
            TasksListMenu.invite_friend_callback
        )
    )
    dp.register_callback_query_handler(
        ios_app_task,
        Text(
            equals=TasksListMenu.ios_app_callback
        )
    )