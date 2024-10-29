from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Query,
)
from aiocryptopay import AioCryptoPay, Networks
from typing_extensions import Annotated
from datetime import datetime
from typing import Union, AsyncIterable
from starlette import status as HTTPStatus
from sqlalchemy import select, update, BigInteger
from decimal import Decimal
from sqlalchemy.ext.asyncio import (
    AsyncSession
)
from services.errors_reporter import Reporter
from services import exceptions

from database.core import (
    core
)
from common.dtos import (
    UserCreate,
    # BalanceWithdraw,
    WithdrawalStatus,
    CompletePretzelTask,
    TransferToken
)
from database.models.models import (
    Users,
    Withdrawals,
    PretzelTasks,
    Workers,
    Transactions
)
from schemas.schemas import (
    BaseUser,
    BaseWithdrawal,
    BasePretzelTask,
    PretzelRewards,
    BaseWorker,
    BaseTransaction
)
from services import exceptions
from schemas.base import DataStructure
from utils import utils
from config import settings


user_router = APIRouter()


@user_router.post("/create_user")
async def create_user(
        parameters: UserCreate,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    data_scheme = BaseUser().model_validate(
        parameters.model_dump()
    )

    user = await session.get(
        Users,
        parameters.telegram_id
    )

    if user:
        return await Reporter(
            exception=exceptions.ItemExists,
            message="User already exist"
        )._report()

    data_scheme.created_at = utils.timestamp()

    session.add(
        Users(
            **data_scheme.model_dump()
        )
    )

    await session.commit()
    await session.close()

    result.data = data_scheme.model_dump()
    result._status = HTTPStatus.HTTP_201_CREATED

    return result


@user_router.get("/{telegram_id}")
async def get_user(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    result.data = user.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    await session.close()

    return result


@user_router.get("/{telegram_id}/balance")
async def get_balance(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    await session.close()

    user_model = user.as_model()

    result.data = {
        "balance": user_model.balance,
        "pretzels": user_model.pretzels
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/current_withdrawal")
async def get_withdrawal(
        parameters: WithdrawalStatus,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    withdrawal = await session.get(
        Withdrawals,
        parameters.withdrawal_id
    )

    if not withdrawal:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Withdrawal not found"
        )._report()

    await session.close()

    result.data = withdrawal.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.get("/{telegram_id}/total_withdrawals")
async def total_withdrawals(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    user_withdrawals = await session.execute(
        select(
            Withdrawals
        ).filter(
            Withdrawals.user_id == telegram_id
        ).filter(
            Withdrawals.status == "sent"
        )
    )

    total_withdrawals: float = 0

    for withdrawal in user_withdrawals.scalars().all():
        total_withdrawals += withdrawal.amount

    await session.close()

    result.data = {
        "total_withdrawals": total_withdrawals
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.put("/{telegram_id}/increase_balance")
async def increase_balance(
        telegram_id: int,
        amount: float,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    user.balance += Decimal(
        amount
    )

    await session.commit()
    await session.close()

    result.data = {
        "balance": float(
            f"{user.balance:.1f}"
        )
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.put("/{telegram_id}/decrease_balance")
async def decrease_balance(
        telegram_id: int,
        amount: float,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    if user.balance < amount:
        user.balance = 0
    else:
        user.balance -= Decimal(
            amount
        )

    await session.commit()
    await session.close()

    result.data = {
        "balance": float(
            f"{user.balance:.1f}"
        )
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/{telegram_id}/complete_task")
async def complete_task(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    task_id: int = 0
    reward: bool = False

    for i, v in user.completed_tasks.items():
        if int(i) >= task_id:
            task_id = int(i) + 1

    user.completed_tasks[task_id] = {
        "task_id": task_id,
        "completed_at": utils.timestamp()
    }
    user.balance += Decimal(
        0.1
    )

    if not task_id:

        if user.referred_by:

            referrer = await session.get(
                Users,
                user.referred_by
            )

            if referrer:
                referrer.balance += Decimal(
                    0.25
                )
                reward = True
                referrer.referred_friends = referrer.referred_friends + [telegram_id]

    await session.execute(
        update(
            Users
        ).filter(
            Users.telegram_id == telegram_id
        ).values(
            {
                "completed_tasks": user.completed_tasks
            }
        )
    )

    await session.commit()
    await session.close()

    result.data = {
        "completed_tasks": user.completed_tasks,
        "about": {
            "referrer_id": user.referred_by,
            "reward": reward
        }
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.get("/{telegram_id}/pretzels_task")
async def check_pretzel_task(
        telegram_id: int,
        task: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    tasks: list = [i for i in PretzelRewards().model_dump()]

    if task not in tasks:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Task is not found."
        )._report()

    allowed: bool = False
    onetime_task: bool = False
    unique_task: bool = False
    status: str = "undefined"

    query = await session.execute(
        select(
            PretzelTasks
        ).filter(
            PretzelTasks.user_id == telegram_id
        ).filter(
            PretzelTasks.status == "pending"
        ).filter(
            PretzelTasks.task == task
        )
    )
    user_task = query.scalars().first()

    if task in ["join_channel", "follow_twitter"]:

        query = await session.execute(
            select(
                PretzelTasks
            ).filter(
                PretzelTasks.user_id == telegram_id
            ).filter(
                PretzelTasks.status.in_(
                    ["pending", "approved"]
                )
            ).filter(
                PretzelTasks.task == task
            )
        )
        onetime_task = query.scalars().first()

    elif task in ["retweet_post"]:

        query = await session.execute(
            select(
                PretzelTasks
            ).filter(
                PretzelTasks.user_id == telegram_id
            ).filter(
                PretzelTasks.status.in_(
                    ["pending", "approved", "declined"]
                )
            ).filter(
                PretzelTasks.task == task
            )
        )
        unique_task = query.scalars().first()

    for j in [user_task, onetime_task, unique_task]:
        if j:
            status = j.status

    if not user_task:
        allowed = True

    if onetime_task or unique_task:
        allowed = False

    result.data = {
        "allowed": allowed,
        "status": status,
        "task": task
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result

@user_router.post("/{telegram_id}/pretzels_task")
async def pretzels_task(
        telegram_id: int,
        parameters: CompletePretzelTask,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    tasks: list = [i for i in PretzelRewards().model_dump()]

    if parameters.task not in tasks:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Task is not found."
        )._report()

    onetime_task: bool = False
    unique_task: bool = False

    if parameters.task in ["join_channel", "follow_twitter"]:

        query = await session.execute(
            select(
                PretzelTasks
            ).filter(
                PretzelTasks.user_id == telegram_id
            ).filter(
                PretzelTasks.status.in_(
                    ["pending", "approved"]
                )
            ).filter(
                PretzelTasks.task == parameters.task
            )
        )
        onetime_task = query.scalars().all()

    elif parameters.task in ["retweet_post"]:

        query = await session.execute(
            select(
                PretzelTasks
            ).filter(
                PretzelTasks.user_id == telegram_id
            ).filter(
                PretzelTasks.status.in_(
                    ["pending", "approved", "declined"]
                )
            ).filter(
                PretzelTasks.task == parameters.task
            )
        )
        unique_task = query.scalars().all()

    query = await session.execute(
        select(
            PretzelTasks
        ).filter(
            PretzelTasks.user_id == telegram_id
        ).filter(
            PretzelTasks.status == "pending"
        ).filter(
            PretzelTasks.task == parameters.task
        )
    )
    user_task = query.scalars().all()

    if user_task or onetime_task or unique_task:
        return await Reporter(
            exception=exceptions.ItemExists,
            message="The task has been already completed."
        )._report()

    task = BasePretzelTask(
        user_id=telegram_id,
        **parameters.model_dump()
    )
    task.id = utils._uuid()
    task.created_at = utils.timestamp()
    task.updated_at = task.created_at

    session.add(
        PretzelTasks(
            **task.model_dump()
        )
    )

    await session.commit()
    await session.close()

    result.data = {
        "id": task.id,
        "user_id": user.telegram_id,
        "username": f"@{user.username}" if user.username else "None",
        "task": PretzelRewards().model_dump()[
            parameters.task
        ]["title"],
        "payload": parameters.payload
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.get("/{telegram_id}/completed_tasks")
async def completed_tasks(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    completed_today: int = 0
    total_completed: int = len(
        user.completed_tasks
    )
    today = utils._today()
    end_of_today = today + 86400

    for i, v in user.completed_tasks.items():
        if v["completed_at"] in range(today, end_of_today):
            completed_today += 1

    await session.close()

    result.data = {
        "completed_today": completed_today,
        "total_completed": total_completed
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/{telegram_id}/withdraw")
async def withdraw_balance(
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    if user.balance < 1.2:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The balance must be > 1.2 to withdraw."
        )._report()

    if user.pretzels["balance"] < 3:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="To withdraw funds you need at least 3 pretzels."
        )._report()

    data_scheme = BaseWithdrawal(
        id=utils._uuid(),
        user_id=telegram_id,
        amount=float(user.balance),
        created_at=utils.timestamp()
    )

    user.pretzels["balance"] -= 3
    user.pretzels["redeemed"] += 3

    await session.execute(
        update(
            Users
        ).filter(
            Users.telegram_id == user.telegram_id
        ).values(
            {
                "pretzels": user.pretzels
            }
        )
    )

    session.add(
        Withdrawals(
            **data_scheme.model_dump()
        )
    )

    user.balance = 0
    user.current_withdrawal = data_scheme.id

    await session.commit()
    await session.close()

    result.data = data_scheme.model_dump()
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/{telegram_id}/gift_pretzel")
async def gift_pretzel(
        telegram_id: int,
        target_user_id: int,
        request: Request,
        amount: int = Query(
            gt=0,
            default=0
        ),
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    if telegram_id == target_user_id:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Can't transfer pretzels to own account"
        )._report()

    user = await session.get(
        Users,
        telegram_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    target_user = await session.get(
        Users,
        target_user_id
    )

    if not target_user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Target user not found"
        )._report()

    if user.pretzels["balance"] < amount:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="You don't have enough Pretzels."
        )._report()

    target_user.pretzels["balance"] += amount
    user.pretzels["balance"] -= amount
    user.pretzels["gifted"] += amount

    await session.execute(
        update(
            Users
        ).filter(
            Users.telegram_id == target_user_id
        ).values(
            {
                "pretzels": target_user.pretzels
            }
        )
    )
    await session.execute(
        update(
            Users
        ).filter(
            Users.telegram_id == telegram_id
        ).values(
            {
                "pretzels": user.pretzels
            }
        )
    )

    await session.commit()
    await session.close()

    result.data = {
        "telegram_id": telegram_id,
        "target_user_id": target_user_id,
        "amount": amount
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


# @user_router.post("/workers")
# async def update_workers(
#         parameters: BaseWorker,
#         request: Request,
#         session: AsyncSession = Depends(
#             core.create_sa_session
#         )
# ) -> Union[DataStructure]:
#     result = DataStructure()
#
#     iteration = await session.get(
#         Workers,
#         parameters.index
#     )
#
#     if iteration:
#         return await Reporter(
#             exception=exceptions.ItemNotFound,
#             message="Iteration exists"
#         )._report()
#
#     session.add(
#         Workers(
#             **parameters.model_dump()
#         )
#     )
#
#     await session.commit()
#     await session.close()
#
#     result.data = parameters.model_dump()
#     result._status = HTTPStatus.HTTP_200_OK
#
#     return result


@user_router.post("/{telegram_id}/transfer_funds")
async def transfer_funds(
        telegram_id: int,
        parameters: TransferToken,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    crypto_bot = AioCryptoPay(
        token=parameters.token,
        network=Networks.MAIN_NET
    )

    try:
        await crypto_bot.get_me()
    except:
        return await Reporter(
            exception=exceptions.UnautorizedException
        )._report()

    query = await session.execute(
        select(
            Withdrawals
        ).filter(
            Withdrawals.user_id == telegram_id
        ).filter(
            Withdrawals.status == "approved"
        )
    )
    withdrawal = query.scalars().first()

    if not withdrawal:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="No approved withdrawals."
        )._report()

    withdrawal.status = "sent"

    try:
        spend_id = utils._uuid()
        transfer_response = await crypto_bot.transfer(
            user_id=withdrawal.user_id,
            asset="USDT",
            amount=float(withdrawal.amount),
            spend_id=spend_id
        )
        session.add(
            Transactions(
                **BaseTransaction(
                    transfer_id=transfer_response.transfer_id,
                    withdrawal_id=withdrawal.id,
                    timestamp=utils.timestamp(),
                    spend_id=spend_id
                ).model_dump()
            )
        )
    except:
        withdrawal.status = "failed"


    user = await session.get(
        Users,
        telegram_id
    )
    username: str = "None"

    if user and user.username:
        username = f"@{user.username}"

    withdrawal.updated_at = utils.timestamp()

    await session.commit()
    await session.close()

    result.data = {
        "message_id": withdrawal.message_id,
        "status": withdrawal.status,
        "updated_at": utils.to_date(
            withdrawal.updated_at
        ),
        "request": {
            "id": withdrawal.id,
            "user_id": withdrawal.user_id,
            "username": username,
            "amount": withdrawal.amount
        }
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result

