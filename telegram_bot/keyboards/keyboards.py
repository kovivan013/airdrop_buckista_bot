from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton
)
from typing import Union


def default_reply_keyboard(
        one_time_keyboard: bool = True,
        resize_keyboard: bool = True,
        row_width: int = 2
) -> Union[ReplyKeyboardMarkup]:
    return ReplyKeyboardMarkup(
        one_time_keyboard=one_time_keyboard,
        resize_keyboard=resize_keyboard,
        row_width=row_width
    )


def default_inline_keyboard(
        row_width: int = 2
) -> Union[InlineKeyboardMarkup]:
    return InlineKeyboardMarkup(
        row_width=row_width
    )


class Base:

    home: str = "🏠Home"
    check_referral: str = "Submit my referral code"

    home_callback: str = "home_callback"
    check_referral_callback: str = "check_referral_callback"


class HomeMenu(Base):

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.home,
                callback_data=cls.home_callback
            )
        )

        return keyboard


class DescriptionMenu:

    airdrop: str = "BioMatrix Airdrop"
    welcome_gift: str = "Welcome Gift"
    # welcome_gift: str = "Join Channel"
    balance: str = "My Balance"

    airdrop_callback: str = "airdrop_callback"
    welcome_gift_callback: str = "welcome_gift_callback"
    # welcome_gift_callback: str = "https://t.me/mrbuckista"
    balance_callback: str = "balance_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.airdrop,
                callback_data=cls.airdrop_callback
            ),
            InlineKeyboardButton(
                text=cls.welcome_gift,
                callback_data=cls.welcome_gift_callback
            ),
            InlineKeyboardButton(
                text=cls.balance,
                callback_data=cls.balance_callback
            )
        )

        # keyboard.add(
        #     InlineKeyboardButton(
        #         text=cls.airdrop,
        #         callback_data=cls.airdrop_callback
        #     )
        # )
        # keyboard.add(
        #     InlineKeyboardButton(
        #         text=cls.welcome_gift,
        #         url=cls.welcome_gift_callback
        #     ),
        #     InlineKeyboardButton(
        #         text=cls.balance,
        #         callback_data=cls.balance_callback
        #     )
        # )

        return keyboard


class WelcomeGiftMenu(DescriptionMenu):

    upoy_bot: str = "uPoY Bot"
    join_channel: str = "Join Channel"
    follow_twitter: str = "Follow Twitter"

    upoy_bot_callback: str = "upoy_bot"
    join_channel_callback: str = "join_channel"
    follow_twitter_callback: str = "follow_twitter"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            # InlineKeyboardButton(
            #     text=cls.upoy_bot,
            #     callback_data=cls.upoy_bot_callback
            # ),
            InlineKeyboardButton(
                text=cls.join_channel,
                callback_data=cls.join_channel_callback
            ),
            InlineKeyboardButton(
                text=cls.follow_twitter,
                callback_data=cls.follow_twitter_callback
            )
        )

        return keyboard

    @classmethod
    def welcome_gift_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.welcome_gift,
                callback_data=cls.welcome_gift_callback
            )
        )

        return keyboard


class TasksListMenu(Base):

    web_app: str = "Web APP"
    android_app: str = "Android APP"
    ios_app: str = "IOS APP"
    invite_friend: str = "Invite a Friend"

    web_app_callback: str = "web_app_callback"
    android_app_callback: str = "android_app_callback"
    ios_app_callback: str = "ios_app_callback"
    invite_friend_callback: str = "invite_friend_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.web_app,
                callback_data=cls.web_app_callback
            ),
            InlineKeyboardButton(
                text=cls.android_app,
                callback_data=cls.android_app_callback
            ),
            InlineKeyboardButton(
                text=cls.ios_app,
                callback_data=cls.ios_app_callback
            ),
            InlineKeyboardButton(
                text=cls.invite_friend,
                callback_data=cls.invite_friend_callback
            ),
            InlineKeyboardButton(
                text=cls.home,
                callback_data=cls.home_callback
            )
        )

        return keyboard


class WebAppTasksMenu(Base):

    to_web_app: str = "Go to the Web APP"

    web_app_link: str = "https://app.biomatrix.ai/refer?code=ULKY8S"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.to_web_app,
                url=cls.web_app_link
            ),
            InlineKeyboardButton(
                text=cls.check_referral,
                callback_data=cls.check_referral_callback
            )
        )

        return keyboard


class AndroidAppTasksMenu(Base):

    download_android_app: str = "Download the Android APP"

    android_app_link: str = "https://play.google.com/store/apps/details?id=com.actechnology.biomatrix"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.download_android_app,
                url=cls.android_app_link
            ),
            InlineKeyboardButton(
                text=cls.check_referral,
                callback_data=cls.check_referral_callback
            )
        )

        return keyboard


class IOSAppTasksMenu(Base):

    download_ios_app: str = "Download the IOS APP"

    ios_app_link: str = "https://apps.apple.com/es/app/biomatrix/id6482980838"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.download_ios_app,
                url=cls.ios_app_link
            ),
            InlineKeyboardButton(
                text=cls.check_referral,
                callback_data=cls.check_referral_callback
            )
        )

        return keyboard


class UPOYBotTaskMenu(Base):

    start_bot: str = "Start uPoY Bot"
    submit_link: str = "Submit my Invitation Link"

    bot_link: str = "https://t.me/uPoYAITokenBot/uPoY?startapp=ref_IZCwami4"
    submit_invite_link_callback: str = "submit_invite_link_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.start_bot,
                url=cls.bot_link
            ),
            InlineKeyboardButton(
                text=cls.submit_link,
                callback_data=cls.submit_invite_link_callback
            )
        )

        return keyboard


class JoinChannelTaskMenu(Base):

    go_to_channel: str = "Go to our Channel"
    submit_username: str = "Submit my Username"

    channel_link: str = "https://t.me/mrbuckista"
    submit_username_callback: str = "submit_username_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.go_to_channel,
                url=cls.channel_link
            ),
            InlineKeyboardButton(
                text=cls.submit_username,
                callback_data=cls.submit_username_callback
            )
        )

        return keyboard


class FollowTwitterTaskMenu(Base):

    go_to_twitter: str = "Go to our Twitter"
    submit_profile_name: str = "Submit my Profile Name"

    twitter_link: str = "https://x.com/mrbuckista"
    submit_profile_name_callback: str = "submit_profile_name_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.go_to_twitter,
                url=cls.twitter_link
            ),
            InlineKeyboardButton(
                text=cls.submit_profile_name,
                callback_data=cls.submit_profile_name_callback
            )
        )

        return keyboard


class InviteMenu:

    invite_friends: str = "Invite friends"

    invite_friends_link: str = "https://t.me/share/url?text=%0A%F0%9F%8F%86%20Unlimited%20Prize%20Pool%20%0A%F0%9F%94%A5%20100%25%20Free%20Rewards&url=https://t.me/officialMrBuckista_bot?start%3D{}"

    @classmethod
    def keyboard(
            cls,
            user_id: int
    ) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.invite_friends,
                url=cls.invite_friends_link.format(
                    user_id
                )
            )
        )

        return keyboard


class WithdrawMenu:

    withdraw: str = "💸Withdraw"
    accept_withdraw: str = "Accept"
    decline_withdraw: str = "Decline"

    withdraw_callback: str = "withdraw_callback"
    accept_withdraw_callback: str = "accept_callback"
    decline_withdraw_callback: str = "decline_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.withdraw,
                callback_data=cls.withdraw_callback
            )
        )

        return keyboard

    @classmethod
    def control(
            cls,
            withdrawal_id: str
    ) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.accept_withdraw,
                callback_data=f"{withdrawal_id}_{cls.accept_withdraw_callback}"
            ),
            InlineKeyboardButton(
                text=cls.decline_withdraw,
                callback_data=f"{withdrawal_id}_{cls.decline_withdraw_callback}"
            )
        )

        return keyboard


class PretzelsMenu:

    accept_pretzels: str = "Accept"
    decline_pretzels: str = "Decline"

    withdraw_callback: str = "withdraw_callback"
    accept_pretzels_callback: str = "accept_pretzels"
    decline_pretzels_callback: str = "decline_pretzels"

    @classmethod
    def control(
            cls,
            task_id: str
    ) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.accept_pretzels,
                callback_data=f"{task_id}_{cls.accept_pretzels_callback}"
            ),
            InlineKeyboardButton(
                text=cls.decline_pretzels,
                callback_data=f"{task_id}_{cls.decline_pretzels_callback}"
            )
        )

        return keyboard

class AdminMenu(Base):

    admin: str = "⚒️ Admin"
    overview: str = "Overview"
    user_data: str = "User Data"
    lucky_draw: str = "Lucky Draw"
    top_referrers: str = "Top Referrers"
    cashier: str = "Cashier"

    admin_callback: str = "admin_callback"
    overview_callback: str = "overview_callback"
    user_data_callback: str = "user_data_callback"
    lucky_draw_callback: str = "lucky_draw_callback"
    top_referrers_callback: str = "top_referrers_callback"
    cashier_callback: str = "cashier_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.overview,
                callback_data=cls.overview_callback
            ),
            InlineKeyboardButton(
                text=cls.user_data,
                callback_data=cls.user_data_callback
            ),
            InlineKeyboardButton(
                text=cls.lucky_draw,
                callback_data=cls.lucky_draw_callback
            ),
            InlineKeyboardButton(
                text=cls.top_referrers,
                callback_data=cls.top_referrers_callback
            ),
            InlineKeyboardButton(
                text=cls.cashier,
                callback_data=cls.cashier_callback
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=cls.home,
                callback_data=cls.home_callback
            )
        )

        return keyboard

    @classmethod
    def admin_menu(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.admin,
                callback_data=cls.admin_callback
            )
        )

        return keyboard

    @classmethod
    def pay_button(
            cls,
            amount: float,
            invoice_url: str
    ) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=f"💸 Pay ${amount:.1f}",
                url=invoice_url
            ),
            InlineKeyboardButton(
                text=cls.admin,
                callback_data=cls.admin_callback
            )
        )

        return keyboard


class CashierMenu(AdminMenu):

    main_wallet: str = "Main Wallet"
    change_wallet: str = "Change Wallet"
    deposit: str = "Deposit"
    weekly_report: str = "Weekly Report"

    main_wallet_callback: str = "main_wallet_callback"
    change_wallet_callback: str = "change_wallet_callback"
    deposit_callback: str = "deposit_callback"
    weekly_report_callback: str = "weekly_report_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(
            row_width=1
        )

        keyboard.add(
            InlineKeyboardButton(
                text=cls.deposit,
                callback_data=cls.deposit_callback
            ),
            InlineKeyboardButton(
                text=cls.main_wallet,
                callback_data=cls.main_wallet_callback
            ),
            InlineKeyboardButton(
                text=cls.weekly_report,
                callback_data=cls.weekly_report_callback
            )
        )

        return keyboard

    @classmethod
    def change_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.change_wallet,
                callback_data=cls.change_wallet_callback
            )
        )

        return keyboard

    @classmethod
    def replaced_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.main_wallet,
                callback_data=cls.main_wallet_callback
            ),
            InlineKeyboardButton(
                text=cls.admin,
                callback_data=cls.admin_callback
            )
        )

        return keyboard