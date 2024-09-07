from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):

    enter_password = State()
    admin_panel = State()
    overview = State()
    user_data = State()
    lucky_user = State()
    lucky_amount = State()
    top_referrers = State()


class ReferralStates(StatesGroup):

    submit_referral = State()
    checked_code = State()
    withdraw_address = State()