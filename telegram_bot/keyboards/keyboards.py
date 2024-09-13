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
    join_channel: str = "Join Channel"
    balance: str = "My Balance"

    airdrop_callback: str = "airdrop_callback"
    join_channel_link: str = "https://t.me/mrbuckista"
    balance_callback: str = "balance_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(
                text=cls.airdrop,
                callback_data=cls.airdrop_callback
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=cls.join_channel,
                url=cls.join_channel_link
            ),
            InlineKeyboardButton(
                text=cls.balance,
                callback_data=cls.balance_callback
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




class AdminMenu(Base):

    overview: str = "Overview"
    user_data: str = "User Data"
    lucky_draw: str = "Lucky Draw"
    top_referrers: str = "Top Referrers"

    overview_callback: str = "overview_callback"
    user_data_callback: str = "user_data_callback"
    lucky_draw_callback: str = "lucky_draw_callback"
    top_referrers_callback: str = "top_referrers_callback"

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
                text=cls.home,
                callback_data=cls.home_callback
            )
        )

        return keyboard