import pytz
import jwt

from datetime import datetime, timedelta
from schemas.schemas import CryptoFactoryException
from config import settings
from uuid import uuid4
from services import exceptions
from fastapi import Request


def timestamp(
        tz: str = "Asia/Singapore"
) -> int:
    pst = pytz.timezone(
        tz
    )
    now = datetime.now(pst)

    return int(
        now.timestamp()
    )


def _uuid() -> str:
    return str(
        uuid4()
    )


def _today(
        tz: str = "Asia/Singapore"
):
    pst = pytz.timezone(
        tz
    )
    now = datetime.now(pst)
    midnight = now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    timestamp = int(
        midnight.timestamp()
    )

    return timestamp


def decode_exception(exc: str):

    return CryptoFactoryException(
        status=int(exc.split(']')[0][1:]),
        message=f"{exc.split('] ')[1].replace('_', ' ').capitalize()}."
    )


def to_date(
        timestamp: int,
        tz: str = "Asia/Singapore"
) -> str:

    pst = pytz.timezone(
            tz
        )

    return str(datetime.fromtimestamp(
        timestamp, pst
    ))


def month_start(
        tz: str = "Asia/Singapore"
) -> int:
    pst = pytz.timezone(
        tz
    )
    now = datetime.now(pst)

    return int(datetime(
        now.year, now.month, 1
    ).timestamp())


def week_start(
        tz: str = "Asia/Singapore"
) -> int:
    pst = pytz.timezone(
        tz
    )
    now = datetime.now(pst)

    week_start = now - timedelta(
        days=now.weekday()
    )

    return int(week_start.replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()
)


def collect_data(
        cls,
        token: str
) -> dict:
    try:
        return jwt.decode(
            token,
            options={
                "verify_signature": False
            }
        )
    except:
        raise exceptions.UnautorizedException


def encode_data(
        data: dict
) -> str:
    return jwt.encode(
        data,
        settings.SIGN_KEY
    )

