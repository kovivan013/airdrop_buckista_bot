from typing import Optional, Union
from .base import Base
from pydantic import BaseModel

from schemas.schemas import (
    BaseUser,
    BaseWithdrawal,
    BaseTransaction,
    BasePretzelTask,
    BaseSettings,
    BaseRally,
    BaseRallyUser,
    BaseWorker
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
    Numeric,
    SmallInteger,
    ARRAY
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
    referred_friends: Mapped[ARRAY] = mapped_column(
        ARRAY(BigInteger),
        nullable=False
    )
    created_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    referred_by: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    pretzels: Mapped[JSON] = mapped_column(
        JSON,
        # nullable=False
    )

    def as_model(self) -> Union[BaseUser]:
        return BaseUser().model_validate(
            self.as_dict()
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
    amount: Mapped[Numeric] = mapped_column(
        Numeric,
        nullable=False
    )
    status: Mapped[String] = mapped_column(
        String,
        nullable=False,
        default="pending"
    )
    created_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    updated_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    message_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )

    def as_model(self) -> Union[BaseWithdrawal]:
        return BaseWithdrawal().model_validate(
            self.as_dict()
        )


class PretzelTasks(Base):

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
        nullable=False,
        default=0
    )
    task: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    payload: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    status: Mapped[String] = mapped_column(
        String,
        nullable=False,
        default="pending"
    )
    created_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    updated_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )

    def as_model(self) -> Union[BasePretzelTask]:
        return BasePretzelTask().model_validate(
            self.as_dict()
        )

class Transactions(Base):

    transfer_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    withdrawal_id: Mapped[String] = mapped_column(
        String,
        nullable=False
    )
    timestamp: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    spend_id: Mapped[String] = mapped_column(
        String,
        nullable=False
    )

    def as_model(self) -> Union[BaseTransaction]:
        return BaseTransaction().model_validate(
            self.as_dict()
        )


class Settings(Base):

    key: Mapped[String] = mapped_column(
        String,
        primary_key=True,
        index=True
    )
    value: Mapped[JSON] = mapped_column(
        JSON,
        nullable=False
    )

    def as_model(self) -> Union[BaseSettings]:
        return BaseSettings().model_validate(
            self.as_dict()
        )


class Rallys(Base):

    round: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    admin_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    start_time: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    end_time: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    allowed_users: Mapped[ARRAY] = mapped_column(
        ARRAY(BigInteger),
        nullable=False
    )
    created_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    updated_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )

    def as_model(self) -> Union[BaseRally]:
        return BaseRally().model_validate(
            self.as_dict()
        )


class RallyUsers(Base):

    participant: Mapped[String] = mapped_column(
        String,
        primary_key=True,
        index=True
    )
    round: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    sequence: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )
    joined_at: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False
    )

    def as_model(self) -> Union[BaseRallyUser]:
        return BaseRallyUser().model_validate(
            self.as_dict()
        )


class Workers(Base):

    index: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    worker_id: Mapped[SmallInteger] = mapped_column(
        SmallInteger,
        nullable=False
    )
    status: Mapped[SmallInteger] = mapped_column(
        SmallInteger,
        nullable=False
    )
    response: Mapped[String] = mapped_column(
        String
    )

    def as_model(self) -> Union[BaseWorker]:
        return BaseWorker().model_validate(
            self.as_dict()
        )