from typing import Optional, Union
from .base import Base
from pydantic import BaseModel

from schemas.schemas import (
    BaseUser,
    BaseWithdrawal
)
from sqlalchemy.orm import (
    mapped_column,
    Mapped
)
from sqlalchemy import (
    Integer,
    String,
    BigInteger,
    JSON,
    Numeric
)


class Users(Base):

    telegram_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    username: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    balance: Mapped[Numeric] = mapped_column(
        Numeric,
        nullable=False
    )
    current_withdrawal: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    completed_tasks: Mapped[JSON] = mapped_column(
        JSON,
        nullable=False
    )
    referred_friends: Mapped[Integer] = mapped_column(
        Integer,
        nullable=False
    )


class Withdrawals(Base):

    id: Mapped[String] = mapped_column(
        String,
        primary_key=True,
        index=True
    )
    user_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    admin_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        default=0
    )
    ton_address: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    amount: Mapped[Numeric] = mapped_column(
        Numeric,
        nullable=False
    )
    status: Mapped[String] = mapped_column(
        String,
        nullable=False,
        default="pending"
    )