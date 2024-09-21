import asyncio
import requests

from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Query,
)
from common.classes import Wallet
from config import settings
from typing_extensions import Annotated
from datetime import datetime
from typing import Union, AsyncIterable
from starlette import status as HTTPStatus
from sqlalchemy import select, update, BigInteger, func
from sqlalchemy.ext.asyncio import (
    AsyncSession
)
from services.errors_reporter import Reporter

from database.core import (
    core
)
from database.models.models import (
    Transactions,
    TestWithdrawals,
    Users
)
from schemas.schemas import (
    BaseTransaction,
    BaseWithdrawal
)
from TonTools import TonCenterClient
from services import exceptions
from schemas.base import DataStructure
from utils import utils


payment_router = APIRouter()


@payment_router.post("/mnemonics")
async def set_mnemonics(
        string: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
):
    result = DataStructure()

    if len(string.strip().split(" ")) != 24:

        return await Reporter(
            exception=exceptions.ValidationException,
            message="The mnemonic phrase must contain 24 words."
        )._report()

    settings.MNEMONICS = string.split(" ")
    result._status = HTTPStatus.HTTP_200_OK

    return result

# @payment_router.get("/")
# async def transfer_usdt(
#         to_addr: str,
#         amount: float,
#         request: Request,
#         session: AsyncSession = Depends(
#             core.create_sa_session
#         )
# ):
#     result = DataStructure()
#
#     if not settings.MNEMONICS:
#
#         return await Reporter(
#             exception=exceptions.UnautorizedException,
#             message="Incorrect mnemonics."
#         )._report()
#
#     provider = TonCenterClient()
#     wallet = Wallet(
#         mnemonics=settings.MNEMONICS,
#         version='v3r2',
#         provider=provider
#     )
#
#     user_wallet = await utils.check_wallet(
#         address=to_addr
#     )
#
#     if user_wallet.success:
#
#         exchange_rate = await utils.collect_ton_exchange_rate(
#             amount=amount
#         )
#
#         if exchange_rate.success:
#
#             response = await wallet.transfer_ton(
#                 destination_address=to_addr,
#                 amount=exchange_rate.data["value"],
#                 message="Buckista Withdraw"
#             )
#
#             print(response.dict())
#             if response.status == 200:
#
#                 await asyncio.sleep(60)
#
#                 payment_status: int = 0
#                 t_data: dict = {}
#                 transactions = requests.get(
#                     url=f"https://tonapi.io/v2/blockchain/accounts/{wallet.address}/transactions?limit=100"
#                 )
#
#                 if transactions.status_code == 200:
#
#                     for transaction in transactions.json()["transactions"]:
#                         if transaction["in_msg"]["decoded_body"]["seqno"] == response.seqno:
#                             t_data = transaction
#                             break
#
#                 if t_data:
#                     if t_data["out_msgs"]:
#
#                         result._status = HTTPStatus.HTTP_200_OK
#                         result.data = t_data
#                         return t_data
#
#                 print(t_data)
#             return response.dict()
#         return exchange_rate.as_dict()
#     return user_wallet.as_dict()


# @payment_router.post("/transactions")
# async def add_transaction(
#
#         request: Request,
#         session: AsyncSession = Depends(
#             core.create_sa_session
#         )
# ):
#     result = DataStructure()
#
#
#
#     return result

# @payment_router.patch("/transactions/{transaction_hash}")
# async def update_transaction(
#         transaction_hash: str,
#         request: Request,
#         status: int = Query(
#             0,
#             gt=-1,
#             lt=3
#         ),
#         session: AsyncSession = Depends(
#             core.create_sa_session
#         )
# ):
#     result = DataStructure()
#
#     transaction = await session.get(
#         Transactions,
#         transaction_hash
#     )
#
#     if not transaction:
#         return await Reporter(
#             exception=exceptions.ItemNotFound,
#             message="Transaction not found."
#         )._report()
#
#     if transaction.status != 0:
#         return await Reporter(
#             exception=exceptions.ItemNotFound,
#             message="Unable to update the transaction status."
#         )._report()
#
#     transaction.status = status
#
#     await session.commit()
#     await session.close()
#
#     result.data = transaction.as_model()
#     result._status = HTTPStatus.HTTP_200_OK
#
#     return result

@payment_router.post("/transactions")
async def process_transactions(
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
):
    result = DataStructure()

    if settings.TRANSFERRING:
        return await Reporter(
            exception=exceptions.BadRequest,
            message="Funds are being transferred."
        )._report()

    query = await session.execute(
        select(
            TestWithdrawals
        ).filter(
            TestWithdrawals.status == "approved"
        ).limit(10)
    )
    withdrawals = query.scalars().all()

    if withdrawals:
        settings.TRANSFERRING = True

    for index, withdrawal in enumerate(withdrawals):
        print(index)
        transfer_response = await utils.transfer_usdt(
            to_addr=withdrawal.ton_address,
            amount=withdrawal.amount
        )

        withdrawal.status = "failed"

        if transfer_response.transaction_created:

            session.add(
                Transactions(
                    **BaseTransaction(
                        hash=transfer_response.data["hash"],
                        withdrawal_id=withdrawal.id,
                        success=transfer_response.success,
                        timestamp=utils.timestamp()
                    ).dict()
                )
            )

            if transfer_response.success:

                withdrawal.status = "sent"

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
                "updated_at": withdrawal.updated_at,
                "request": {
                    "id": withdrawal.id,
                    "user_id": withdrawal.user_id,
                    "username": username,
                    "ton_address": withdrawal.ton_address,
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


@payment_router.patch("/reset_withdrawal")
async def transfer_failed(
        withdrawal_id: str,
        request: Request,
        session: AsyncSession = Depends(
            core.create_sa_session
        )
):
    result = DataStructure()

    withdrawal = await session.get(
        TestWithdrawals,
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

    withdrawal.status = "pending"
    withdrawal.updated_at = utils.timestamp()

    user.current_withdrawal = withdrawal.id

    await session.commit()
    await session.close()

    # result.data = withdrawal.as_dict()
    result._status = HTTPStatus.HTTP_200_OK

    return result
