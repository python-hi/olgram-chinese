from dotenv import load_dotenv
import os

load_dotenv()


class InstanceSettings:
    @classmethod
    def _get_env(cls, parameter: str) -> str:
        parameter = os.getenv(parameter, None)
        if not parameter:
            raise ValueError(f"{parameter} not defined in ENV")
        return parameter

    @classmethod
    def token(cls) -> str:
        """
        Token instance бота
        :return:
        """
        return cls._get_env("INSTANCE_TOKEN")

    @classmethod
    def super_chat_id(cls) -> int:
        """
        ID чата, в который бот пересылает сообщения
        Это может быть личный чат (ID > 0) или общий чат (ID < 0)
        :return:
        """
        return int(cls._get_env("INSTANCE_SUPER_CHAT_ID"))

    @classmethod
    def start_text(cls) -> str:
        """
        Этот текст будет отправляться пользователю по команде /start
        :return:
        """
        return cls._get_env("INSTANCE_START_TEXT")

    @classmethod
    def redis_path(cls) -> str:
        """
        Путь до БД redis
        :return:
        """
        return cls._get_env("INSTANCE_REDIS_PATH")
