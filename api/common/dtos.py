from pydantic import BaseModel, Field
from typing import List


class UserCreate(BaseModel):

    telegram_id: int = 0
    username: str = ""
    referred_by: int = 0


class WithdrawalStatus(BaseModel):

    withdrawal_id: str = ""


class TransferToken(BaseModel):

    token: str = ""


class CompletePretzelTask(BaseModel):

    task: str = ""
    payload: str = ""


class RallyCreate(BaseModel):

    admin_id: int = 0
    start_time: int = 0
    end_time: int = 0
    allowed_users: List[int] = []