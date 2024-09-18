import requests
import pytz
import asyncio

from datetime import datetime, timedelta
from schemas.base import DataStructure
from starlette import status as HTTPStatus
from services import exceptions
from common.classes import Wallet
from config import settings
from typing import Union
from TonTools import TonCenterClient
from uuid import uuid4


def timestamp() -> int:
    pst = pytz.timezone(
        'America/Los_Angeles'
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

async def collect_ton_exchange_rate(
        amount: float
) -> Union[DataStructure]:
    result = DataStructure()
    response = requests.get(
        url=f"https://swap.tonkeeper.com/v2/swap/calculate?fromAsset=0%3Ab113a994b5024a16719f69139328eb759596c38a25f59028b146fecdc3621dfe&toAsset=ton&fromAmount={int(amount * 1000000)}&provider=stonfi"
    )

    result._status = response.status_code
    result.message = "USDT exchange rate."

    if response.status_code == 200:

        result.data = {
            "value": int((response.json())["trades"][0]["stonfiRawTrade"]["toAmount"]) / 1000000000
        }

    result.transaction_created = False

    return result

async def check_wallet(
        address: str
) -> Union[DataStructure]:
    result = DataStructure()
    response = requests.get(
        url=f"https://tonapi.io/v2/blockchain/accounts/{address}"
    )

    result._status = response.status_code

    if response.status_code == 200:
        result.data = response.json()
    else:
        result.message = response.json()["error"]

    result.transaction_created = False

    return result


async def transfer_usdt(
        to_addr: str,
        amount: float
) -> Union[DataStructure]:
    result = DataStructure()

    if not settings.MNEMONICS:

        return DataStructure(
            status=exceptions.UnautorizedException.status_code,
            message="Incorrect mnemonics."
        )

    provider = TonCenterClient()
    wallet = Wallet(
        mnemonics=settings.MNEMONICS,
        version='v3r2',
        provider=provider
    )

    user_wallet = await check_wallet(
        address=to_addr
    )

    if user_wallet.success:

        exchange_rate = await collect_ton_exchange_rate(
            amount=amount
        )

        if exchange_rate.success:

            response = await wallet.transfer_ton(
                destination_address=to_addr,
                amount=exchange_rate.data["value"],
                message="Buckista Withdraw"
            )

            print(response.dict())
            if response.status == 200:

                result.transaction_created: bool = False

                for i in range(10):
                    print("FOR", i)
                    await asyncio.sleep(6)

                    transactions = requests.get(
                        url=f"https://tonapi.io/v2/blockchain/accounts/{wallet.address}/transactions?limit=100"
                    )

                    if transactions.status_code == 200:
                        print("SUCCESS TRANSR FOR", i)
                        for transaction in transactions.json()["transactions"]:
                            try:
                                if transaction["in_msg"]["decoded_body"]["seqno"] == response.seqno:
                                    print("SUCCESS CREATED", i)
                                    result.transaction_created = True
                                    t_data = transaction
                                    break
                            except:
                                continue
                        else:
                            continue

                    if result.transaction_created:
                        break

                if result.transaction_created:

                    result.data.update({
                        "hash": t_data["hash"]
                    })
                    print(t_data["out_msgs"], bool(t_data["out_msgs"]))
                    if t_data and t_data["out_msgs"]:

                        result._status = HTTPStatus.HTTP_200_OK

                return result

            result._status = HTTPStatus.HTTP_400_BAD_REQUEST
            result.message = "Something went wrong, try again later."

            return result
        return exchange_rate
    return user_wallet
