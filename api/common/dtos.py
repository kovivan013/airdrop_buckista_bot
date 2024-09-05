from pydantic import BaseModel


class UserCreate(BaseModel):

    telegram_id: int = 0
    username: str = ""