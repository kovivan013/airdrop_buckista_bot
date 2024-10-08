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
    # BalanceWithdraw,
    WithdrawalStatus,
    TransferToken
)
from database.models.models import (
    Users,
    Withdrawals,
    Transactions,
    PretzelTasks
)
from schemas.schemas import (
    BaseUser,
    BaseWithdrawal,
    BaseTransaction,
    BasePretzelTask,
    PretzelRewards
)
from services import exceptions
from schemas.base import DataStructure
from utils import utils
from config import settings


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
    total_pretzels: int = 0
    redeemed_pretzels: int = 0
    today = utils._today()
    end_of_today = today + 86400

    for user in all_users:

        total_completed_tasks += len(
            user.completed_tasks
        )

        total_pretzels += user.pretzels["balance"] + user.pretzels["redeemed"]
        redeemed_pretzels += user.pretzels[
            "redeemed"
        ]

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
        "total_refferals": total_refferals,
        "total_pretzels": total_pretzels,
        "redeemed_pretzels": redeemed_pretzels
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
        message_id: int,
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
    withdrawal.message_id = message_id
    withdrawal.updated_at = utils.timestamp()

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
        message_id: int,
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
    withdrawal.message_id = message_id
    withdrawal.updated_at = utils.timestamp()

    user.balance = user.balance + withdrawal.amount
    user.current_withdrawal = "0"

    await session.commit()
    await session.close()

    result.data = withdrawal.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    return result

@admin_router.get("/weekly_report")
async def weekly_report(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    query = await session.execute(
        select(
            Withdrawals
        )
    )
    withdrawals = query.scalars().all()

    rows: list = []

    for withdrawal in withdrawals:

        if withdrawal.created_at > utils.week_start() - 604800 and withdrawal.created_at < utils.week_start():

            status_values: dict = {
                "sent": "Sent",
                "declined": "Failed",
                "pending": "Open"
            }

            if withdrawal.status in status_values:

                row = [
                    withdrawal.user_id,
                    withdrawal.amount,
                    status_values[
                        withdrawal.status
                    ],
                    utils.to_date(
                        withdrawal.updated_at or withdrawal.created_at
                    )
                ]
                rows.append(
                    row
                )

    await session.close()

    result.data = {
        "values": [
            "User ID",
            "Withdrawal Amount",
            "Payment Status",
            "Last Change"
        ],
        "rows": rows
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result

@admin_router.get("/cashier_statistics")
async def cashier_statistics(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    query = await session.execute(
        select(
            Transactions
        )
    )
    transactions = query.scalars().all()
    total_transfer: float = 0
    this_month: float = 0
    this_week: float = 0

    month_start: int = utils.month_start()
    week_start: int = utils.week_start()

    for transaction in transactions:
        withdrawal = await session.get(
            Withdrawals,
            transaction.withdrawal_id
        )

        if withdrawal:

            amount = float(
                withdrawal.amount
            )

            total_transfer += amount

            if transaction.timestamp >= month_start:
                this_month += amount
            if transaction.timestamp >= week_start:
                this_week += amount

    await session.close()

    result.data = {
        "total_transfer": total_transfer,
        "this_month": this_month,
        "this_week": this_week
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/transfer_funds")
async def transfer_funds(
        parameters: TransferToken,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
) -> Union[DataStructure]:
    result = DataStructure()

    crypto_bot = AioCryptoPay(
        token=parameters.token,
        network=Networks.MAIN_NET
    )

    try:
        await crypto_bot.get_me()
    except:
        return await Reporter(
            exception=exceptions.UnautorizedException
        )._report()

    if settings.TRANSFERRING:
        return await Reporter(
            exception=exceptions.BadRequest,
            message="Funds are being transferred."
        )._report()

    query = await session.execute(
        select(
            Withdrawals
        ).filter(
            Withdrawals.status == "approved"
        ).limit(10)
    )
    withdrawals = query.scalars().all()

    if withdrawals:
        settings.TRANSFERRING = True

    for index, withdrawal in enumerate(withdrawals):
        withdrawal.status = "sent"
        try:
            spend_id = utils._uuid()
            transfer_response = await crypto_bot.transfer(
                user_id=withdrawal.user_id,
                asset="USDT",
                amount=float(withdrawal.amount),
                spend_id=spend_id
            )
            session.add(
                Transactions(
                    **BaseTransaction(
                        transfer_id=transfer_response.transfer_id,
                        withdrawal_id=withdrawal.id,
                        timestamp=utils.timestamp(),
                        spend_id=spend_id
                    ).model_dump()
                )
            )
        except:
            withdrawal.status = "failed"


        user = await session.get(
            Users,
            withdrawal.user_id
        )
        username: str = "None"

        if user and user.username:
            username = f"@{user.username}"

        result.data.update({
            index: {
                "message_id": withdrawal.message_id,
                "status": withdrawal.status,
                "updated_at": utils.to_date(
                    withdrawal.updated_at
                ),
                "request": {
                    "id": withdrawal.id,
                    "user_id": withdrawal.user_id,
                    "username": username,
                    "amount": withdrawal.amount
                }
            }
        })
        withdrawal.updated_at = utils.timestamp()

        await session.commit()

    await session.close()

    settings.TRANSFERRING = False
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/approve_pretzel_task")
async def approve_pretzel_tasks(
        admin_id: int,
        task_id: str,
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

    task = await session.get(
        PretzelTasks,
        task_id
    )

    if not task:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown task."
        )._report()

    if task.status in ["approved", "declined"]:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The task can't be approved."
        )._report()

    user = await session.get(
        Users,
        task.user_id
    )

    task.status = "approved"
    task.admin_id = admin_id
    task.updated_at = utils.timestamp()

    task_data = PretzelRewards().model_dump()[
        task.task
    ]

    reward = task_data["reward"]

    user.pretzels["balance"] += reward

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

    await session.commit()
    await session.close()

    result.data = {
        "user_id": user.telegram_id,
        "username": f"@{user.username}" if user.username else "None",
        "task": task_data["title"],
        "reward": reward,
        "payload": task.payload,
        "status": task.status
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/decline_pretzel_task")
async def decline_pretzel_task(
        admin_id: int,
        task_id: str,
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

    task = await session.get(
        PretzelTasks,
        task_id
    )

    if not task:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="Unknown task."
        )._report()

    if task.status in ["approved", "declined"]:
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The task can't be declined."
        )._report()

    user = await session.get(
        Users,
        task.user_id
    )

    task_data = PretzelRewards().model_dump()[
        task.task
    ]

    task.status = "declined"
    task.admin_id = admin_id
    task.updated_at = utils.timestamp()

    await session.commit()
    await session.close()

    result.data = {
        "user_id": user.telegram_id,
        "username": f"@{user.username}" if user.username else "None",
        "task": task_data["title"],
        "payload": task.payload,
        "status": task.status
    }
    result._status = HTTPStatus.HTTP_200_OK

    return result


@admin_router.post("/reset_withdrawal")
async def transfer_failed(
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
            message="Unknown withdrawal."
        )._report()

    if withdrawal.status != "failed":
        return await Reporter(
            exception=exceptions.NotAcceptable,
            message="The withdrawal can't be updated."
        )._report()

    user = await session.get(
        Users,
        withdrawal.user_id
    )

    if not user:
        return await Reporter(
            exception=exceptions.ItemNotFound,
            message="User not found"
        )._report()

    withdrawal.status = "pending"
    withdrawal.updated_at = utils.timestamp()

    user.current_withdrawal = withdrawal.id

    await session.commit()
    await session.close()

    result._status = HTTPStatus.HTTP_200_OK

    return result