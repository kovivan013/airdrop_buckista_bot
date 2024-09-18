import os
from dotenv import load_dotenv


load_dotenv()

class Settings:

    uri: str = "postgresql+asyncpg://{}:{}@{}:{}/{}"
    name: str = os.getenv("NAME")
    host: str = os.getenv("HOST")
    port: int = os.getenv("PORT")
    user: str = os.getenv("USER")
    password: str = os.getenv("PASSWORD")

    WALLET_ADDRESS: str = ""
    MNEMONICS: list = "broom argue artwork cup sheriff there clerk rely clerk casino world choice laptop hazard siren convince click place abstract always catalog prevent vanish garment".split(" ")

    TRANSFERRING: bool = False

    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    @property
    def url(self) -> str:
        return self.uri.format(
            "postgres",
            self.password,
            self.host,
            self.port,
            "postgres"
        )

settings = Settings()