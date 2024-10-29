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

    BASE_API_URL: str = "http://api.buckista.com"

    CRYPTOBOT_TOKEN: str
    ADMINS_CHAT: int = -1002430116586
    # ADMINS_CHAT: int = -4556254373
    OFFICIAL_CHANNEL: int = -1002202854690
    PRETZELS_CHAT: int = -1002299302859

settings = Settings()
storage = MemoryStorage()

bot = Bot(
    token=settings.BOT_TOKEN
)
dp = Dispatcher(
    bot=bot,
    storage=storage
)