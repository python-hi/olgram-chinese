from aiogram import Bot
import hashlib

from olgram.settings import ServerSettings


def path_for_bot(token: str) -> str:
    return "/" + hashlib.md5(token.encode("UTF-8")).hexdigest()


def url_for_bot(token: str) -> str:
    return f"https://{ServerSettings.hook_host()}:{ServerSettings.hook_port()}" + path_for_bot(token)


async def register_token(token: str) -> bool:
    """
    Зарегистрировать токен
    :param token: токен
    :return: получилось ли
    """
    bot = Bot(token)
    res = await bot.set_webhook(url_for_bot(token))
    await bot.session.close()
    return res


async def unregister_token(token: str):
    """
    Удалить токен
    :param token: токен
    :return:
    """
    bot = Bot(token)
    await bot.delete_webhook()
