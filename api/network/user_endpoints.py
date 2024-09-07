from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Query,
)
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
    BalanceWithdraw
)
from database.models.models import (
    Users,
    Withdrawals
)
from schemas.schemas import (
    BaseUser,
    BaseWithdrawal
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

    await session.close()

    result.data = user.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

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
        "balance": user_model.balance
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.get("/current_withdrawal")
async def get_withdrawal(
        withdrawal_id: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    withdrawal = await session.get(
        Withdrawals,
        withdrawal_id
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
            Withdrawals.status == "approved"
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


@user_router.post("/{telegram_id}/refer_friend")
async def refer_friend(
        referrer_id: int,
        telegram_id: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    referrer = await session.get(
        Users,
        referrer_id
    )
    user = await session.get(
        Users,
        telegram_id
    )

    if not referrer:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown referrer."
        )._report()

    if user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="This user has been already referred."
        )._report()

    if telegram_id in referrer.referred_friends:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="This user has been already referred."
        )._report()

    if referrer_id == telegram_id:
        return await Reporter(
            exception=exceptions.UnautorizedException,
            message="Prohibited referrer."
        )._report()

    referrer.referred_friends = referrer.referred_friends + [telegram_id]

    await session.commit()
    await session.close()

    result.data = {
        "referred_friends": len(
            referrer.referred_friends
        )
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/{telegram_id}/complete_task")
async def complete_task(
        telegram_id: int,
        task_id: int,
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

    if task_id < 1 or task_id > 3:
        return await Reporter(
            exception=exceptions.InvalidInputData,
            message="Only 3 tasks."
        )._report()

    user.completed_tasks[task_id] = True

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

    result.data = user.completed_tasks
    result._status = HTTPStatus.HTTP_200_OK

    return result


@user_router.post("/{telegram_id}/withdraw")
async def withdraw_balance(
        telegram_id: int,
        parameters: BalanceWithdraw,
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
        return Reporter(
            exception=exceptions.NotAcceptable,
            message="The balance must be > 1 to withdraw."
        )

    data_scheme = BaseWithdrawal().model_validate(
        parameters.model_dump()
    )

    data_scheme.id = utils._uuid()
    data_scheme.user_id = telegram_id
    data_scheme.amount = float(user.balance)
    data_scheme.created_at = utils.timestamp()

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
