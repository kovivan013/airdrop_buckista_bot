from pydantic import BaseModel
from typing import Dict, List


class Pretzels(BaseModel):

    balance: int = 0
    redeemed: int = 0
    gifted: int = 0

class BaseUser(BaseModel):

    telegram_id: int = 0
    username: str = ""
    balance: float = 0
    current_withdrawal: str = ""
    completed_tasks: Dict[int, dict] = {}
    referred_friends: List[int] = []
    created_at: int = 0
    referred_by: int = 0
    pretzels: Pretzels = Pretzels()


class BaseWithdrawal(BaseModel):

    id: str = ""
    user_id: int = 0
    admin_id: int = 0
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


class UPOYBotTask(BaseModel):

    title: str = "uPoY Bot"
    reward: int = 3


class JoinChannelTask(BaseModel):

    title: str = "Join Channel"
    reward: int = 1


class FollowTwitterTask(BaseModel):

    title: str = "Follow Twitter"
    reward: int = 2


class BasePretzelTask(BaseModel):

    id: str = ""
    user_id: int = 0
    admin_id: int = 0
    task: str = ""
    payload: str = ""
    status: str = "pending"
    created_at: int = 0
    updated_at: int = 0


class PretzelRewards(BaseModel):

    upoy_bot: UPOYBotTask = UPOYBotTask()
    join_channel: JoinChannelTask = JoinChannelTask()
    follow_twitter: FollowTwitterTask = FollowTwitterTask()


class BaseWorker(BaseModel):

    index: int = 0
    worker_id: int = 0
    status: int = 0
    response: str = ""
