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
from sqlalchemy import select, update, BigInteger, func
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
    BalanceWithdraw,
    WithdrawalStatus
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


admin_router = APIRouter()


@admin_router.get("/overview")
async def overview(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    all_users = (
        await session.execute(
            select(
                Users
            )
        )
    ).scalars().all()

    total_users = len(
        all_users
    )
    registered_users: int = 0
    registered_today: int = 0
    total_completed_tasks: int = 0
    total_refferals: int = 0
    today = utils._today()
    end_of_today = today + 86400

    for user in all_users:

        total_completed_tasks += len(
            user.completed_tasks
        )

        total_refferals += len(
            user.referred_friends
        )

        if len(user.completed_tasks):
            registered_users += 1

            if user.created_at in range(today, end_of_today):
                registered_today += 1

    await session.close()

    result.data = {
        "total_users": total_users,
        "registered_users": registered_users,
        "registered_today": registered_today,
        "total_completed_tasks": total_completed_tasks,
        "total_refferals": total_refferals
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.get("/top_referrers")
async def top_referrers(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    users = await session.execute(
        select(
            Users
        )
    )

    refferers: list = []

    for user in users.scalars().all():
        refferers.append(
            {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "reffered_friends": len(
                    user.referred_friends
                )
            }
        )

    top_referrers = sorted(
        refferers,
        key=lambda x: x['reffered_friends'],
        reverse=True
    )

    for i, v in zip(range(10), top_referrers):
        result.data.update(
            {
                i: v
            }
        )

    await session.close()

    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/approve_withdrawal")
async def approve_withdrawal(
        admin_id: int,
        withdrawal_id: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    admin = await session.get(
        Users,
        admin_id
    )

    if not admin:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    withdrawal = await session.get(
        Withdrawals,
        withdrawal_id
    )

    if not withdrawal:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown withdrawal."
        )._report()

    if withdrawal.status in ["approved", "declined"]:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The withdrawal can't be approved."
        )._report()

    user = await session.get(
        Users,
        withdrawal.user_id
    )

    withdrawal.status = "approved"
    withdrawal.admin_id = admin_id

    user.current_withdrawal = "0"

    await session.commit()
    await session.close()

    result.data = withdrawal.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/decline_withdrawal")
async def decline_withdrawal(
        admin_id: int,
        withdrawal_id: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    admin = await session.get(
        Users,
        admin_id
    )

    if not admin:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    withdrawal = await session.get(
        Withdrawals,
        withdrawal_id
    )

    if not withdrawal:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown withdrawal."
        )._report()

    if withdrawal.status in ["approved", "declined"]:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The withdrawal can't be declined."
        )._report()

    user = await session.get(
        Users,
        withdrawal.user_id
    )

    withdrawal.status = "declined"
    withdrawal.admin_id = admin_id

    user.balance = user.balance + withdrawal.amount
    user.current_withdrawal = "0"

    await session.commit()
    await session.close()

    result.data = withdrawal.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    return result