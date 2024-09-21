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
        text=f"🎉 Hello <b>{event.from_user.username if event.from_user.username else 'User'}</b>! \n"
             "==============================\n"
             "\n"
             "🚨 Join the <b>BioMatrix Daily Airdrop</b> to earn rewards:\n"
             "\n"
             "🔹 <b>Task Reward</b>\n"
             "🔸 Unlimited Prize Pool\n"
             "🔸 0.2 USDT + 100 POY for using APP\n"
             "🔸 0.3 USDT for each valid invitation\n"
             "\n"
             "🔹 <b>Lucky Draw</b>\n"
             "🔸 Monthly\n"
             "🔸 500 USDT in prizes\n"
             "🔸 100 random winners\n"
             "\n"
             "📅 <b>End Date</b>: 31 December 2024\n"
             "🚀 <b>Distribution Time</b>: Within 7 business days\n"
             "\n"
             "==============================\n"
             "⬇️ <i>Click <b>BioMatrix Airdrop</b> and explore the tasks available</i>\n"
             "⬇️ <i>Click <b>My Balance</b> to withdraw your rewards at any time</i>\n",
        reply_markup=DescriptionMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def start(
        event: Message,
        state: FSMContext
) -> None:
    referrer_id: int = 0

    try:
        referrer_id = int(
            event.text.split()[1]
        )
    except:
        pass

    requests.post(
        url=f"{settings.BASE_API_URL}/user/create_user",
        json={
            "telegram_id": event.from_user.id,
            "username": event.from_user.username if event.from_user.username else "",
            "referred_by": referrer_id
        }
    )
    await event.answer(
        text=f"🎉 Hello <b>{event.from_user.username if event.from_user.username else 'User'}</b>! \n"
             "==============================\n"
             "\n"
             "🚨 Join the <b>BioMatrix Daily Airdrop</b> to earn rewards:\n"
             "\n"
             "🔹 <b>Task Reward</b>\n"
             "🔸 Unlimited Prize Pool\n"
             "🔸 0.2 USDT + 100 POY for using APP\n"
             "🔸 0.3 USDT for each valid invitation\n"
             "\n"
             "🔹 <b>Lucky Draw</b>\n"
             "🔸 Monthly\n"
             "🔸 500 USDT in prizes\n"
             "🔸 100 random winners\n"
             "\n"
             "📅 <b>End Date</b>: 31 December 2024\n"
             "🚀 <b>Distribution Time</b>: Within 7 business days\n"
             "\n"
             "==============================\n"
             "⬇️ <i>Click <b>BioMatrix Airdrop</b> and explore the tasks available</i>\n"
             "⬇️ <i>Click <b>My Balance</b> to withdraw your rewards at any time</i>\n",
        reply_markup=DescriptionMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def tasks_list(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="🎯 <b>Complete Tasks & Earn Rewards!</b>\n"
             "\n"
             "💎 Get <b>0.2 USDT</b> for using our Web APP\n"
             "💎 Get <b>0.2 USDT</b> for using our iOS APP\n"
             "💎 Get <b>0.2 USDT</b> for using our Android APP\n"
             "💎 Get <b>0.3 USDT</b> for each valid invitation",
        reply_markup=TasksListMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def user_balance(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}"
    ).json()["data"]
    current_withdrawal = requests.post(
        url=f"{settings.BASE_API_URL}/user/current_withdrawal",
        json={
            "withdrawal_id": response['current_withdrawal']
        }
    ).json()
    total_withdrawals = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/total_withdrawals"
    ).json()["data"]
    await event.message.answer(
        text=f"💰 <b>Your Current Balance</b>: {response['balance']} USDT\n"
             "\n"
             f"➡️ <b>Withdrawal Request</b>: {current_withdrawal['data']['amount'] if current_withdrawal['status'] == 200 else 0} USDT\n"
             f"🤑 <b>Total Withdrawals</b>: {total_withdrawals['total_withdrawals']} USDT\n"
             "\n"
             f"👥 <b>Friends Referred</b>: {len(response['referred_friends'])}\n"
             "\n"
             "<i>Please note that your withdrawal requires the Telegram Wallet to be activated</i>"
        ,
        reply_markup=WithdrawMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def submit_referral(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await ReferralStates.submit_referral.set()
    await event.message.answer_photo(
        photo=open("images/refcode.jpg", "rb"),
        caption="✅ Click Settings\n"
             "✅ Scroll To The Referral Code Section\n"
             "✅ Copy your Referral Code\n"
             "\n"
             "Then submit your *Referral Code*:\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="Markdown"
    )

@handle_error
async def check_referral(
        event: Message,
        state: FSMContext
) -> None:
    await ReferralStates.checked_code.set()
    response = requests.get(
            f"https://rds-service.bio-matrix.com/redeemReferCode/{event.text}"
    )

    if response.status_code in range(200, 300):
        response_model = BaseReferral().model_validate(
            response.json()
        )
    else:
        await state.finish()
        return await event.answer(
            text="❗️ We can't check your referral code now! Please try again later.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )

    if response_model.Succ:
        if response_model.refer_code_status == ResponseMessages.valid_code:
            response = requests.post(
                url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/complete_task"
            ).json()

            if response["status"] == 200:

                if response["data"]["about"]["reward"]:
                    try:
                        await bot.send_message(
                            chat_id=response["data"]["about"]["referrer_id"],
                            text="🎉 <b>New Referral Registered!</b> 🎉\n"
                                 "\n"
                                 "👤 A new user has registered using your referral link.\n"
                                 "\n"
                                 "💸 You received a reward of 0.3 USDT\n",
                            parse_mode="HTML"
                        )
                    except:
                        pass

            return await event.answer(
                text="🎉 Your referral code is valid! Your balance has been increased by 0.2 USDT.",
                reply_markup=HomeMenu.keyboard(),
                parse_mode="Markdown"
            )
        elif response_model.refer_code_status == ResponseMessages.already_redeemed:
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
        text="📝 <b>Use BioMatrix Web App</b>\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ <b>Register</b> on the <b>Web APP</b>\n"
             "2️⃣ Copy the <b>Referral Code</b> from the APP\n"
             "3️⃣ <b>Submit</b> your Referral Code\n"
             "\n"
             "💰 <i>You will earn 0.2 USDT and 100 POY for completing this task</i>",
        reply_markup=WebAppTasksMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def android_app_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 <b>Use BioMatrix Android App</b>\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ <b>Register</b> on the <b>Android APP</b>\n"
             "2️⃣ Copy the <b>Referral Code</b> from the APP\n"
             "3️⃣ <b>Submit</b> your Referral Code\n"
             "\n"
             "💰 <i>You will earn 0.2 USDT and 100 POY for completing this task</i>",
        reply_markup=AndroidAppTasksMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def ios_app_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 <b>Use BioMatrix IOS App</b>\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ <b>Register</b> on the <b>IOS APP</b>\n"
             "2️⃣ Copy the <b>Referral Code</b> from the APP\n"
             "3️⃣ <b>Submit</b> your Referral Code\n"
             "\n"
             "💰 <i>You will earn 0.2 USDT and 100 POY for completing this task</i>",
        reply_markup=IOSAppTasksMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def enter_ton_address(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await ReferralStates.withdraw_address.set()
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}"
    ).json()["data"]

    current_withdrawal = requests.post(
        url=f"{settings.BASE_API_URL}/user/current_withdrawal",
        json={
            "withdrawal_id": response['current_withdrawal']
        }
    ).json()

    if current_withdrawal["status"] == 200 and current_withdrawal["data"]["status"] in ["pending", "declined"]:
        await state.finish()
        return await event.message.answer(
            text="❌ You cannot submit a new withdrawal request until your latest one has been processed. Thank you for your patience.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )
    elif float(response["balance"]) < 1:
        await state.finish()
        return await event.message.answer(
            text="❌ *Minimum withdrawal amount 1 USDT*",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )

    return await event.message.answer(
        text=f"💵 <b>Withdrawal Amount</b>: {response['balance']} USDT\n"
             "\n"
             "<i>We only accept USDT-TON address from your Telegram Wallet</i>\n"
             "\n"
             "Submit your <b>USDT-TON Address</b>\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def withdraw_balance(
        event: Message,
        state: FSMContext
) -> None:
    withdrawal = requests.post(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/withdraw",
        # json={
        #     "ton_address": event.text
        # }
    ).json()["data"]
    await event.answer(
        text="✅ <b>Withdrawal Request Submitted</b>\n"
             "\n"
             "Your withdrawal request has been successfully submitted. 🎉\n"
             "We will review and process it within <b>7 business days</b>. Thank you for your patience! 😊\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=settings.ADMINS_CHAT,
        text="🆕 <b>New Withdrawal Request</b>\n"
             "\n"
             f"<b>User ID</b>: {event.from_user.id}\n"
             f"<b>Username</b>: {'@' + event.from_user.username if event.from_user.username else 'None'}\n"
             # f"<b>TON Wallet Address</b>: {event.text}\n"
             f"<b>Requested Balance</b>: {withdrawal['amount']} USDT\n",
        reply_markup=WithdrawMenu.control(
            withdrawal_id=withdrawal["id"]
        ),
        parse_mode="HTML"
    )
    await state.finish()

@handle_error
async def invite_friend(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}"
    ).json()["data"]
    await event.message.answer(
        text="🎉 Invite your friends to join our bot and earn rewards! When your friends claim the airdrop, you will receive a reward of <b>0.3 USDT</b>.\n"
             "\n"
             f"🔗 <b>Your Referral Link</b>: https://t.me/officialMrBuckista_bot?start={event.from_user.id}\n"
             f"👥 <b>Friends Referred</b>: {len(response['referred_friends'])}\n"
             "\n"
             "Share this link with your friends and watch your balance grow! 🚀\n",
        reply_markup=InviteMenu.keyboard(
            user_id=event.from_user.id
        ),
        parse_mode="HTML"
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