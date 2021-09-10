from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import SendMessage, WebhookRequestHandler
from aiogram import types
from olgram.models.models import Bot
from aiohttp import web
from asyncio import get_event_loop
from olgram.settings import ServerSettings
from custom import CustomRequestHandler

import logging


logger = logging.getLogger(__name__)


def path_for_bot(bot: Bot) -> str:
    return "/" + str(bot.code)


def url_for_bot(bot: Bot) -> str:
    return f"https://{ServerSettings.hook_host()}:{ServerSettings.hook_port()}" + path_for_bot(bot)


async def register_token(bot: Bot) -> bool:
    """
    Зарегистрировать токен
    :param bot: Бот
    :return: получилось ли
    """
    await unregister_token(bot.token)

    a_bot = AioBot(bot.token)
    res = await a_bot.set_webhook(url_for_bot(bot))
    await a_bot.session.close()
    del a_bot
    return res


async def unregister_token(token: str):
    """
    Удалить токен
    :param token: токен
    :return:
    """
    bot = AioBot(token)
    await bot.delete_webhook()
    await bot.session.close()
    del bot


def main():
    loop = get_event_loop()

    app = web.Application()
    app.router.add_route('*', r"/{name}", CustomRequestHandler, name='webhook_handler')

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    logger.info("Server initialization done")
    site = web.TCPSite(runner, host=ServerSettings.app_host(), port=ServerSettings.app_port())
    return site
