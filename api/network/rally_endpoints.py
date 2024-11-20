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
from common.dtos import (
    RallyCreate
)
from database.core import (
    core
)
from database.models.models import (
    Rallys,
    RallyUsers,
    Users
)
from schemas.schemas import (
    BaseUser,
    BaseWithdrawal,
    BasePretzelTask,
    PretzelRewards,
    BaseWorker,
    BaseTransaction,
    BaseRally,
    BaseRallyUser,
    RallyStatus
)
from services import exceptions
from schemas.base import DataStructure
from utils import utils
from config import settings


rally_router = APIRouter()

@rally_router.get("/")
async def rally_settings(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    query = await session.execute(
        select(
            Rallys
        ).order_by(
            Rallys.round.desc()
        )
    )
    all_rounds = query.scalars().all()

    if all_rounds:
        active_round = all_rounds[0].as_dict()
    else:
        active_round = BaseRally().model_dump()

    rounds: dict = {
        "active": active_round
    }

    for i in all_rounds:
        rounds.update(
            {
                i.round: i.as_dict()
            }
        )

    await session.close()

    result.data = rounds
    result._status = HTTPStatus.HTTP_200_OK

    return result


@rally_router.get("/{round}")
async def get_rally(
        round: int,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    rally = await session.get(
        Rallys,
        round
    )

    if not rally:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Rally not found."
        )._report()

    status = RallyStatus().in_progress

    if rally.end_time <= utils.timestamp():
        status = RallyStatus().ended

    await session.close()

    result.data = rally.as_dict()
    result.data.update(
        {
            "status": status
        }
    )
    result._status = HTTPStatus.HTTP_200_OK

    return result


@rally_router.post("/")
async def new_rally(
        parameters: RallyCreate,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    admin = await session.get(
        Users,
        parameters.admin_id
    )

    if not admin:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    if parameters.start_time <= utils.timestamp():
        return await Reporter(
            exception=exceptions.ValidationException,
            message="Start time must be greater than current time."
        )._report()

    elif parameters.end_time <= parameters.start_time:
        return await Reporter(
            exception=exceptions.ValidationException,
            message="Start time must be less than end time."
        )._report()

    query = await session.execute(
        select(
            Rallys
        ).order_by(
            Rallys.round.desc()
        )
    )
    active_round = query.scalars().first()

    if not active_round:
        active_round = BaseRally()

    if active_round.end_time > utils.timestamp():
        return await Reporter(
            exception=exceptions.ValidationException,
            message="The active round must be finished to create the new one."
        )._report()

    unique_users = list(set(
        parameters.allowed_users
    ))

    for user_id in unique_users:
        allowed_user = await session.get(
            Users,
            user_id
        )

        if not allowed_user:
            parameters.allowed_users.remove(
                user_id
            )

    new_round = BaseRally(
        round=active_round.round + 1,
        **parameters.model_dump()
    )
    new_round.created_at = utils.timestamp()
    new_round.updated_at = new_round.created_at

    session.add(
        Rallys(
            **new_round.model_dump()
        )
    )
    await session.commit()
    await session.close()

    result.data = new_round.model_dump()
    result._status = HTTPStatus.HTTP_200_OK

    return result


