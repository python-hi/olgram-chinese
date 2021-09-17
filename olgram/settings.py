from dotenv import load_dotenv
from abc import ABC
import os


load_dotenv()


class AbstractSettings(ABC):
    @classmethod
    def _get_env(cls, parameter: str, allow_none: bool = False) -> str:
        parameter = os.getenv(parameter, None)
        if not parameter and not allow_none:
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

    @classmethod
    def version(cls):
        return "0.0.3"


class ServerSettings(AbstractSettings):
    @classmethod
    def hook_host(cls) -> str:
        return cls._get_env("WEBHOOK_HOST")

    @classmethod
    def hook_port(cls) -> int:
        return int(cls._get_env("WEBHOOK_PORT"))

    @classmethod
    def app_host(cls) -> str:
        return "olgram"

    @classmethod
    def app_port(cls) -> int:
        return 80

    @classmethod
    def redis_path(cls) -> str:
        """
        Путь до БД redis
        :return:
        """
        return cls._get_env("REDIS_PATH")

    @classmethod
    def use_custom_cert(cls) -> bool:
        use = cls._get_env("CUSTOM_CERT", allow_none=True)
        return use and "true" in use.lower()

    @classmethod
    def priv_path(cls) -> str:
        return "/cert/private.key"

    @classmethod
    def public_path(cls) -> str:
        return "/cert/public.pem"

    @classmethod
    def append_text(cls) -> str:
        return "\n\nЭтот бот создан с помощью @OlgramBot"


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

    @classmethod
    def host(cls) -> str:
        return cls._get_env("POSTGRES_HOST")


TORTOISE_ORM = {
    "connections": {"default": f'postgres://{DatabaseSettings.user()}:{DatabaseSettings.password()}'
                               f'@{DatabaseSettings.host()}/{DatabaseSettings.database_name()}'},
    "apps": {
        "models": {
            "models": ["olgram.models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
