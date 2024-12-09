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
    BOTNET: str
    SIGN_KEY: str

    BASE_API_URL: str = "http://api.buckista.com"

    CRYPTOBOT_TOKEN: str
    ADMINS_CHAT: int = -1002430116586
    # ADMINS_CHAT: int = -4556254373
    OFFICIAL_CHANNEL: int = -1002202854690
    PRETZELS_CHAT: int = -1002299302859


class BotSettings:

    RETWEETING_LINK: str = "https://x.com/mrbuckista/status/1853669490195939766"
    BANNED_USERS: list = []


settings = Settings()
bot_settings = BotSettings()
storage = MemoryStorage()

bot = Bot(
    token=settings.BOT_TOKEN
)
dp = Dispatcher(
    bot=bot,
    storage=storage
)