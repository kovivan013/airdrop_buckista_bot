from pydantic import BaseModel


class BaseUser(BaseModel):

    telegram_id: int = 0
    username: str = ""
    balance: int = 0
    current_withdrawal: int = 0
    completed_tasks: dict = {}
    referred_friends: int = 0


class BaseWithdrawal(BaseModel):

    id: str = ""
    user_id: int = 0
    admin_id: int = 0
    ton_address: str = ""
    amount: float = 0
    status: str = "pending"
