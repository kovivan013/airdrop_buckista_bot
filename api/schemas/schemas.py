from pydantic import BaseModel
from typing import Dict, List


class BaseUser(BaseModel):

    telegram_id: int = 0
    username: str = ""
    balance: float = 0
    current_withdrawal: str = ""
    completed_tasks: Dict[int, dict] = {}
    referred_friends: List[int] = []
    created_at: int = 0
    referred_by: int = 0


class BaseWithdrawal(BaseModel):

    id: str = ""
    user_id: int = 0
    admin_id: int = 0
    ton_address: str = ""
    amount: float = 0
    status: str = "pending"
    created_at: int = 0
    updated_at: int = 0
    message_id: int = 0

class BaseTransaction(BaseModel):

    transfer_id: int = 0
    withdrawal_id: str = ""
    timestamp: int = 0
    spend_id: str = ""


class CryptoFactoryException(BaseModel):

    status: int = 200
    message: str = ""