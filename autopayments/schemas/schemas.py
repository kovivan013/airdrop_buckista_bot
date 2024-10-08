from pydantic import BaseModel
from typing import Dict, List


class BaseTransaction(BaseModel):

    hash: str = ""
    withdrawal_id: str = ""
    success: bool = False
    timestamp: int = 0


class TonTransferResponse(BaseModel):

    status: int = 0
    seqno: int = 0


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


class BaseUser(BaseModel):

    telegram_id: int = 0
    username: str = ""
    balance: float = 0
    current_withdrawal: str = ""
    completed_tasks: Dict[int, dict] = {}
    referred_friends: List[int] = []
    created_at: int = 0
    referred_by: int = 0