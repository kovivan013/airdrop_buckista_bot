from pydantic import BaseModel


class UserCreate(BaseModel):

    telegram_id: int = 0
    username: str = ""
    referred_by: int = 0


# class BalanceWithdraw(BaseModel):
#
#     ton_address: str = ""


class WithdrawalStatus(BaseModel):

    withdrawal_id: str = ""


class TransferToken(BaseModel):

    token: str = ""


class CompletePretzelTask(BaseModel):

    task: str = ""
    payload: str = ""