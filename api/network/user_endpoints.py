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
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from database.core import (
    core
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
        parameters: UserCreat,
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
        result._status = HTTPStatus.HTTP_409_CONFLICT
        return result

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

