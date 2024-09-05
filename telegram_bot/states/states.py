from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminStates(StatesGroup):

    enter_password = State()
    admin_panel = State()


class ReferralStates(StatesGroup):

    submit_referral = State()
    checked_code = State()