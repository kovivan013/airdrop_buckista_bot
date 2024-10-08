from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Query,
)
from uuid import UUID
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
    CompletePretzelTask
)
from database.models.models import (
    Users,
    Withdrawals,
    PretzelTasks
)
from schemas.schemas import (
    BaseUser,
    BaseWithdrawal,
    BasePretzelTask,
    PretzelRewards
)
from services import exceptions
from schemas.base import DataStructure
from utils import utils


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

    if task in ["join_channel", "follow_twitter"]:
        print(1)
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
        onetime_task = query.scalars().all()

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
    user_task = query.scalars().all()

    print(onetime_task, user_task)

    if not user_task:
        allowed = True

    if onetime_task:
        allowed = False

    result.data = {
        "allowed": allowed
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

    if user_task or onetime_task:
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

    if user.balance < 1:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The balance must be > 1 to withdraw."
        )._report()

    if user.pretzels["balance"] < 1:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="To withdraw funds you need at least 1 pretzel."
        )._report()

    data_scheme = BaseWithdrawal(
        id=utils._uuid(),
        user_id=telegram_id,
        amount=float(user.balance),
        created_at=utils.timestamp()
    )

    user.pretzels["balance"] -= 1
    user.pretzels["redeemed"] += 1

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
