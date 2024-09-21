from datetime import datetime, timedelta
from schemas.schemas import CryptoFactoryException
from uuid import uuid4
import pytz


def timestamp() -> int:
    pst = pytz.timezone(
        'Asia/Singapore'
    )
    now = datetime.now(pst)

    return int(
        now.timestamp()
    )

def _uuid() -> str:
    return str(
        uuid4()
    )

def _today():
    pst = pytz.timezone(
        'Asia/Singapore'
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


