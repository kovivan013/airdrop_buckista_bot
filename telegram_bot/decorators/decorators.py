from functools import wraps
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from typing import Any, Callable


def private_message(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[0]

        if message.chat.type == "private":

            return await func(
                *args, **kwargs
            )

    return wrapper


def handle_error(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(
                *args, **kwargs
            )
        except:
            print(f"WARNING | Error during {func} function execution")

    return wrapper