import requests
from aiogram import Dispatcher
import aiohttp
from config import bot, settings
from utils import utils
from aiogram.types import (
    Message,
    CallbackQuery,
    InputFile
)
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from states.states import (
    ReferralStates,
    WelcomeGiftStates,
    PretzelGift
)
from decorators.decorators import (
    private_message,
    handle_error,
    check_pretzel_task,
    check_payload
)
from keyboards.keyboards import (
    DescriptionMenu,
    TasksListMenu,
    WebAppTasksMenu,
    AndroidAppTasksMenu,
    IOSAppTasksMenu,
    InviteMenu,
    WithdrawMenu,
    HomeMenu,
    WelcomeGiftMenu,
    UPOYBotTaskMenu,
    JoinChannelTaskMenu,
    FollowTwitterTaskMenu,
    PretzelsMenu
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
    await event.message.answer_photo(
        photo=open("images/main_menu.jpg", "rb"),
        caption=f"🎉 Hello <b>{event.from_user.username if event.from_user.username else 'User'}</b>! \n"
                "==============================\n"
                "\n"
                "🚨 Join the <b>BioMatrix Daily Airdrop</b> to earn rewards:\n"
                "\n"
                "🔹 <b>Task Reward</b>\n"
                "🔸 Unlimited Prize Pool\n"
                "🔸 0.1 USDT for using APP + up to 100 POY\n"
                "🔸 0.25 USDT for each valid invitation\n"
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
                "⬇️ <i>Click <b>BioMatrix Airdrop</b> for tasks</i>\n"
                "⬇️ <i>Click <b>Welcome Gift</b> for withdrawal tokens</i>\n"
                "⬇️ <i>Click <b>My Balance</b> to withdraw rewards</i>\n",
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
    await event.answer_photo(
        photo=open("images/main_menu.jpg", "rb"),
        caption=f"🎉 Hello <b>{event.from_user.username if event.from_user.username else 'User'}</b>! \n"
                "==============================\n"
                "\n"
                "🚨 Join the <b>BioMatrix Daily Airdrop</b> to earn rewards:\n"
                "\n"
                "🔹 <b>Task Reward</b>\n"
                "🔸 Unlimited Prize Pool\n"
                "🔸 0.1 USDT for using APP + up to 100 POY\n"
                "🔸 0.25 USDT for each valid invitation\n"
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
                "⬇️ <i>Click <b>BioMatrix Airdrop</b> for tasks</i>\n"
                "⬇️ <i>Click <b>Welcome Gift</b> for withdrawal tokens</i>\n"
                "⬇️ <i>Click <b>My Balance</b> to withdraw rewards</i>\n",
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
             "💎 Get <b>0.1 USDT</b> for using our Web APP\n"
             "💎 Get <b>0.1 USDT</b> for using our iOS APP\n"
             "💎 Get <b>0.1 USDT</b> for using our Android APP\n"
             "💎 Get <b>0.25 USDT</b> for each valid invitation",
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
        text=f"🪪 <b>UserID</b>: {event.from_user.id}\n"
             f"\n"
             f"💰 <b>Your Current Balance</b>: {float(response['balance']):.2f} USDT\n"
             "\n"
             f"➡️ <b>Withdrawal Request</b>: {float(current_withdrawal['data']['amount']) if current_withdrawal['status'] == 200 else 0} USDT\n"
             f"🤑 <b>Total Withdrawals</b>: {float(total_withdrawals['total_withdrawals']):.2f} USDT\n"
             "\n"
             f"🧢 <b>Friends Referred</b>: {len(response['referred_friends'])}\n"
             f"🥨 <b>Pretzel</b>: {response['pretzels']['balance']}\n"
             "\n"
             "==============================\n"
             "<i>Withdrawal Notice:</i>\n"
             "\n"
             "- <i>Crypto Bot Wallet activation required</i>\n"
             "- <i>Minimum amount is 1.2 USDT</i>\n"
             "- <i>Sufficient Pretzel needed</i>\n",
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
                                 "💸 You received a reward of 0.25 USDT\n",
                            parse_mode="HTML"
                        )
                    except:
                        pass

            return await event.answer(
                text="🎉 Your referral code is valid! Your balance has been increased by 0.1 USDT.",
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
             "💰 <i>You will earn 0.1 USDT for completing this task</i>",
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
             "💰 <i>You will earn 0.1 USDT for completing this task</i>",
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
             "💰 <i>You will earn 0.1 USDT for completing this task</i>",
        reply_markup=IOSAppTasksMenu.keyboard(),
        parse_mode="HTML"
    )

# @handle_error
# async def enter_ton_address(
#         event: CallbackQuery,
#         state: FSMContext
# ) -> None:
#     await ReferralStates.withdraw_address.set()
#     response = requests.get(
#         url=f"{settings.BASE_API_URL}/user/{event.from_user.id}"
#     ).json()["data"]
#
#     current_withdrawal = requests.post(
#         url=f"{settings.BASE_API_URL}/user/current_withdrawal",
#         json={
#             "withdrawal_id": response['current_withdrawal']
#         }
#     ).json()
#
#     if current_withdrawal["status"] == 200 and current_withdrawal["data"]["status"] in ["pending", "declined"]:
#         await state.finish()
#         return await event.message.answer(
#             text="❌ You cannot submit a new withdrawal request until your latest one has been processed. Thank you for your patience.",
#             reply_markup=HomeMenu.keyboard(),
#             parse_mode="Markdown"
#         )
#     elif float(response["balance"]) < 1:
#         await state.finish()
#         return await event.message.answer(
#             text="❌ *Minimum withdrawal amount 1 USDT*",
#             reply_markup=HomeMenu.keyboard(),
#             parse_mode="Markdown"
#         )
#
#     return await event.message.answer(
#         text=f"💵 <b>Withdrawal Amount</b>: {response['balance']} USDT\n"
#              "\n"
#              "<i>We only accept USDT-TON address from your Telegram Wallet</i>\n"
#              "\n"
#              "Submit your <b>USDT-TON Address</b>\n",
#         reply_markup=HomeMenu.keyboard(),
#         parse_mode="HTML"
#     )

@handle_error
async def withdrawal_id(
        event: Message,
        state: FSMContext
) -> None:
    if event.from_user.id == 1125858430:
        await ReferralStates.withdrawal_id.set()
        await event.answer(
            text="Withdrawal ID, User ID, Amount"
        )

@handle_error
async def resend_withdrawal(
        event: Message,
        state: FSMContext
) -> None:
    data = event.text.split(", ")
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{data[1]}"
    ).json()["data"]
    await bot.send_message(
        chat_id=settings.ADMINS_CHAT,
        text="🆕 <b>New Withdrawal Request</b>\n"
             "\n"
             f"<b>User ID</b>: {data[1]}\n"
             f"<b>Username</b>: {'@' + response['username']}\n"
             f"<b>Requested Balance</b>: {data[2]} USDT\n",
        reply_markup=WithdrawMenu.control(
            withdrawal_id=data[0]
        ),
        parse_mode="HTML"
    )
    await state.finish()

@handle_error
async def welcome_gift_menu(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="🎯 <b>Complete Tasks & Earn Rewards!</b>\n"
             "\n"
             "🥨 Get <b>1 Pretzel</b> by following Channel\n"
             "🥨 Get <b>2 Pretzels</b> by following Twitter\n"
             # "🥨 Get <b>3 Pretzels</b> by following uPoY bot\n"
             "\n"
             "✍️ <i>What are Pretzels used for?</i>\n"
             "🗣 <i>Withdrawal requires sufficient Pretzel.</i>\n",
        reply_markup=WelcomeGiftMenu.keyboard(),
        parse_mode="HTML"
    )

@check_pretzel_task
async def upoy_bot_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 Start BioMatrix uPoY Bot\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ Start uPoY Bot\n"
             "2️⃣ Copy the Invitation link from the Bot\n"
             "3️⃣ Submit your Invitation link here\n"
             "\n"
             "🥨 You will earn 3 Pretzels for completing this task\n",
        reply_markup=UPOYBotTaskMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def submit_invitation_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await WelcomeGiftStates.invitation_link.set()
    async with state.proxy() as data:
        data["task"] = "upoy_bot"
    await event.message.answer(
        text="📝 <b>For example</b>: https://t.me/uPoYAITokenBot/uPoY?startapp=mrbuckista\n"
             "\n"
             "Then submit your <b>Invitation link</b>:\n",
        reply_markup=HomeMenu.keyboard(),
        disable_web_page_preview=True,
        parse_mode="HTML"
    )

@check_pretzel_task
async def join_channel_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    async with state.proxy() as data:
        data["task"] = "join_channel"
    await event.message.answer(
        text="📝 <b>Mr. Buckista Telegram Channel</b>\n"
             "\n"
             "Only 2 steps to complete the task:\n"
             "\n"
             "1️⃣ Join <a href='https://t.me/mrbuckista'>Mr. Buckista Channel</a>\n"
             "2️⃣ <b>Click</b> the <b>button</b> below\n"
             "\n"
             "🥨 <i>You will earn 1 Pretzel for completing this task</i>\n",
        disable_web_page_preview=True,
        reply_markup=JoinChannelTaskMenu.keyboard(),
        parse_mode="HTML"
    )

@check_pretzel_task
async def follow_twitter_task(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await event.message.answer(
        text="📝 <b>Mr. Buckista Twitter</b>\n"
             "\n"
             "Only 3 steps to complete the task:\n"
             "\n"
             "1️⃣ Follow <b>Mr. Buckista</b> Twitter\n"
             "2️⃣ <b>Retweet</b> any post\n"
             "3️⃣ <b>Submit</b> your <b>Twitter profile name</b>\n"
             "\n"
             "🥨 <i>You will earn 2 Pretzels for completing this task</i>\n",
        reply_markup=FollowTwitterTaskMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def submit_profile_name(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    await WelcomeGiftStates.profile_name.set()
    async with state.proxy() as data:
        data["task"] = "follow_twitter"
    await event.message.answer(
        text="📝 <b>For example</b>: https://x.com/mrbuckista\n"
             "\n"
             "Then submit your <b>Twitter Profile Name</b>:\n",
        reply_markup=HomeMenu.keyboard(),
        disable_web_page_preview=True,
        parse_mode="HTML"
    )

@check_payload
@handle_error
async def request_pretzels(
        event: Message,
        state: FSMContext
) -> None:
    automated_tasks: list = ["join_channel"]

    async with state.proxy() as data:
        task =  data["task"]

        if task in automated_tasks:
            payload = task
        else:
            payload = event.text

        response = requests.post(
            url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/pretzels_task",
            json={
                "task": task,
                "payload": payload
            }
        )

    if response.status_code == 200:

        response_data = response.json()["data"]

        if task not in automated_tasks:

            await event.answer(
                text="🎉 Thank you for completing the task. You’ll receive Pretzels soon.",
                reply_markup=HomeMenu.keyboard(),
                parse_mode="HTML"
            )
            await bot.send_message(
                chat_id=settings.PRETZELS_CHAT,
                text=f"🆕 <b>New Pretzel Order</b>\n"
                     f"\n"
                     f"<b>User ID</b>: {response_data['user_id']}\n"
                     f"<b>Username</b>: {response_data['username']}\n"
                     f"<b>Task</b>: {response_data['task']}\n"
                     f"<b>Submitted Info</b>: {response_data['payload']}\n",
                reply_markup=PretzelsMenu.control(
                    task_id=response_data["id"]
                ),
                parse_mode="HTML"
            )

        if task == "join_channel":

            admin_id: int = 995570913

            try:
                is_join = await bot.get_chat_member(
                    settings.OFFICIAL_CHANNEL,
                    event.from_user.id
                )

                if is_join.status not in ["member", "administrator", "creator"]:
                    raise

                await utils.accept_join_task(
                    task_id=response_data["id"],
                    admin_id=admin_id
                )
            except:
                await utils.decline_join_task(
                    task_id=response_data["id"],
                    admin_id=admin_id
                )

        await state.finish()

    elif response.status_code == 409:

        await event.answer(
            text="✅ You've completed this task. If you haven't received your Pretzel, please wait patiently.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )

@handle_error
async def withdraw_balance(
        event: Message,
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

    if current_withdrawal["status"] == 200 and current_withdrawal["data"]["status"] in ["pending", "declined"]:
        await state.finish()
        return await event.message.answer(
            text="❌ You cannot submit a new withdrawal request until your latest one has been processed. Thank you for your patience.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )
    elif float(response["balance"]) < 1.2:
        await state.finish()
        return await event.message.answer(
            text="❌ *Minimum withdrawal amount 1.2 USDT*",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="Markdown"
        )

    withdrawal = requests.post(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/withdraw",
    )

    if withdrawal.status_code == 406:
        await state.finish()
        return await event.message.answer(
            text="❌ *Withdrawal requires 1 Pretzel.*\n"
                 "\n"
                 "How to get Pretzels? Go to *Welcome Gift* and complete tasks.\n",
            reply_markup=WelcomeGiftMenu.welcome_gift_keyboard(),
            parse_mode="Markdown"
        )

    withdrawal_data = withdrawal.json()["data"]

    await event.message.answer(
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
             f"<b>Requested Balance</b>: {withdrawal_data['amount']} USDT\n",
        reply_markup=WithdrawMenu.control(
            withdrawal_id=withdrawal_data["id"]
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
        text="🎉 Invite your friends to join our bot and earn rewards! When your friends claim the airdrop, you will receive a reward of <b>0.25 USDT</b>.\n"
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

@handle_error
async def gift_pretzels(
        event: CallbackQuery,
        state: FSMContext
) -> None:
    user_pretzels = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.from_user.id}"
    ).json()["data"]["pretzels"]

    if user_pretzels["balance"] < 1:

        return await event.message.answer(
            text="🤦 Oh man! You’ve got no Pretzels!\n"
                 "\n"
                 "How to get Pretzels? Go to <b>Welcome Gift</b> and complete tasks.\n",
            reply_markup=WelcomeGiftMenu.welcome_gift_keyboard(),
            parse_mode="HTML"
        )

    await PretzelGift.gift_pretzel_id.set()
    await event.message.answer(
        text="🎁 <b>Gift Pretzel</b>\n"
             "\n"
             "Enter the <b>user ID</b> to whom you want to gift the Pretzel:\n",
        reply_markup=HomeMenu.keyboard(),
        parse_mode="HTML"
    )

@handle_error
async def pretzel_user_id(
        event: Message,
        state: FSMContext
) -> None:
    response = requests.get(
        url=f"{settings.BASE_API_URL}/user/{event.text}"
    )

    if response.status_code != 200 or str(event.from_user.id) == event.text:

        return await event.answer(
            text="🚫 This user does not exist. Please re-enter:\n",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )

    await PretzelGift.pretzel_amount.set()
    async with state.proxy() as data:
        data["user_id"] = int(
            event.text
        )
    await event.answer(
        text=f"🎁 <b>Gift Pretzel</b>\n"
             f"\n"
             f"Enter <b>how many</b> Pretzels you want to gift to user <b>{event.text}</b>:\n",
        parse_mode="HTML"
    )

@handle_error
async def transfer_pretzels(
        event: Message,
        state: FSMContext
) -> None:
    async with state.proxy() as data:
        response = requests.post(
            url=f"{settings.BASE_API_URL}/user/{event.from_user.id}/gift_pretzel?target_user_id={data['user_id']}&amount={event.text}"
        )

    if response.status_code == 200:
        response_data = response.json()["data"]

        await event.answer(
            text=f"🎉 User <b>{response_data['target_user_id']}</b> has received <b>{response_data['amount']} Pretzel{'s' if response_data['amount'] > 1 else ''}</b> that you gifted.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=response_data['target_user_id'],
            text=f"🥨 You have received <b>{response_data['amount']} Pretzel{'s' if response_data['amount'] > 1 else ''}</b> from user <b>{response_data['telegram_id']}</b>.",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )

    elif response.status_code in range(400, 500):
        response_data = response.json()["data"]

        return await event.answer(
            text="⚠️ You don't have enough Pretzels. Please re-enter:",
            reply_markup=HomeMenu.keyboard(),
            parse_mode="HTML"
        )

    await state.finish()


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
        welcome_gift_menu,
        Text(
            equals=DescriptionMenu.welcome_gift_callback
        ),
        state=["*"]
    )
    # dp.register_callback_query_handler(
    #     upoy_bot_task,
    #     Text(
    #         equals=WelcomeGiftMenu.upoy_bot_callback
    #     )
    # )
    dp.register_callback_query_handler(
        join_channel_task,
        Text(
            equals=WelcomeGiftMenu.join_channel_callback
        )
    )
    dp.register_callback_query_handler(
        follow_twitter_task,
        Text(
            equals=WelcomeGiftMenu.follow_twitter_callback
        )
    )
    # dp.register_callback_query_handler(
    #     submit_invitation_task,
    #     Text(
    #         equals=UPOYBotTaskMenu.submit_invite_link_callback
    #     )
    # )
    dp.register_callback_query_handler(
        request_pretzels,
        Text(
            equals=JoinChannelTaskMenu.join_channel_callback
        )
    )
    dp.register_callback_query_handler(
        submit_profile_name,
        Text(
            equals=FollowTwitterTaskMenu.submit_profile_name_callback
        )
    )
    dp.register_callback_query_handler(
        submit_referral,
        Text(
            equals=TasksListMenu.check_referral_callback
        )
    )
    dp.register_message_handler(
        request_pretzels,
        state=[
            WelcomeGiftStates.invitation_link,
            WelcomeGiftStates.username,
            WelcomeGiftStates.profile_name
        ]
    )
    dp.register_message_handler(
        check_referral,
        state=ReferralStates.submit_referral
    )
    dp.register_callback_query_handler(
        withdraw_balance,
        Text(
            WithdrawMenu.withdraw_callback
        )
    )
    dp.register_callback_query_handler(
        gift_pretzels,
        Text(
            WithdrawMenu.gift_pretzel_callback
        )
    )
    dp.register_message_handler(
        pretzel_user_id,
        state=PretzelGift.gift_pretzel_id
    )
    dp.register_message_handler(
        transfer_pretzels,
        state=PretzelGift.pretzel_amount
    )
    # dp.register_message_handler(
    #     withdraw_balance,
    #     state=ReferralStates.withdraw_address
    # )
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
    dp.register_message_handler(
        withdrawal_id,
        commands=["resend"],
        state=["*"]
    )
    dp.register_message_handler(
        resend_withdrawal,
        state=ReferralStates.withdrawal_id
    )

