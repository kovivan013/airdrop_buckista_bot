from pydantic_settings import BaseSettings, SettingsConfigDict
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    BOT_TOKEN: str
    ADMIN_PASSWORD: str

    # BASE_API_URL: str = "http://18.199.174.253"
    BASE_API_URL: str = "http://127.0.0.1:8000"
    # AUTOPAYMENTS_URL: str = "http://127.0.0.1:8000"

    CRYPTOBOT_TOKEN: str = ""
    ADMINS_CHAT: int = -4556254373

settings = Settings()
storage = MemoryStorage()

bot = Bot(
    token=settings.BOT_TOKEN
)
dp = Dispatcher(
    bot=bot,
    storage=storage
)