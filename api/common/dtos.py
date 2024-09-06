from pydantic import BaseModel


class UserCreate(BaseModel):

    telegram_id: int = 0
    username: str = ""


class BalanceWithdraw(BaseModel):

    ton_address: str = ""


class WithdrawalStatus(BaseModel):

    withdrawal_id: str = ""