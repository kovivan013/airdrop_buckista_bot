from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Query,
)
from typing import Dict, Any
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

from database.models.models import (
    Settings
)
from schemas.schemas import (
    BaseSettings
)
from services import exceptions
from schemas.base import DataStructure
from utils import utils
from config import settings


settings_router = APIRouter()

@settings_router.get("/{bot_hash}")
async def load_settings(
        bot_hash: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    bot_settings = await session.get(
        Settings,
        bot_hash
    )

    if not bot_settings:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown bot hash."
        )._report()

    await session.close()

    result.data = bot_settings.value
    result._status = HTTPStatus.HTTP_200_OK

    return result


@settings_router.patch("/{bot_hash}")
async def update_settings(
        bot_hash: str,
        values: Dict[str, Any],
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    bot_settings = await session.get(
        Settings,
        bot_hash
    )

    if not bot_settings:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown bot hash."
        )._report()

    for i, v in values.items():
        bot_settings.value[i] = v

    await session.execute(
        update(
            Settings
        ).filter(
            Settings.key == bot_hash
        ).values(
            {
                "value": bot_settings.value
            }
        )
    )

    await session.commit()
    await session.close()

    result.data = bot_settings.value
    result._status = HTTPStatus.HTTP_200_OK

    return result

