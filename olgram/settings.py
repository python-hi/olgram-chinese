from abc import ABC
from dotenv import load_dotenv
import os


load_dotenv()


class _Settings(ABC):
    @classmethod
    def _get_env(cls, parameter: str) -> str:
        parameter = os.getenv(parameter, None)
        if not parameter:
            raise ValueError(f"{parameter} not defined in ENV")
        return parameter


class OlgramSettings(_Settings):
    @classmethod
    def max_bots_per_user(cls) -> int:
        """
        Максимальное количество ботов у одного пользователя
        :return: int
        """
        return 5


class BotSettings(_Settings):
    @classmethod
    def token(cls) -> str:
        return cls._get_env("BOT_TOKEN")


class DatabaseSettings(_Settings):
    @classmethod
    def user(cls) -> str:
        return cls._get_env("POSTGRES_USER")

    @classmethod
    def password(cls) -> str:
        return cls._get_env("POSTGRES_PASSWORD")

    @classmethod
    def database_name(cls) -> str:
        return cls._get_env("POSTGRES_DB")
