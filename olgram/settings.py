from dotenv import load_dotenv
from abc import ABC
import os


load_dotenv()


class AbstractSettings(ABC):
    @classmethod
    def _get_env(cls, parameter: str) -> str:
        parameter = os.getenv(parameter, None)
        if not parameter:
            raise ValueError(f"{parameter} not defined in ENV")
        return parameter


class OlgramSettings(AbstractSettings):
    @classmethod
    def max_bots_per_user(cls) -> int:
        """
        Максимальное количество ботов у одного пользователя
        :return: int
        """
        return 5


class BotSettings(AbstractSettings):
    @classmethod
    def token(cls) -> str:
        """
        Токен olgram бота
        :return:
        """
        return cls._get_env("BOT_TOKEN")


class DatabaseSettings(AbstractSettings):
    @classmethod
    def user(cls) -> str:
        return cls._get_env("POSTGRES_USER")

    @classmethod
    def password(cls) -> str:
        return cls._get_env("POSTGRES_PASSWORD")

    @classmethod
    def database_name(cls) -> str:
        return cls._get_env("POSTGRES_DB")
