from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):

    enter_password = State()
    admin_panel = State()
    overview = State()
    user_data = State()
    lucky_user = State()
    lucky_amount = State()
    top_referrers = State()
    cashier = State()
    main_wallet = State()
    change_wallet = State()
    invoice_amount = State()


class ReferralStates(StatesGroup):

    withdrawal_id = State()
    submit_referral = State()
    checked_code = State()
    withdraw_address = State()


class WelcomeGiftStates(StatesGroup):

    invitation_link = State()
    username = State()
    profile_name = State()