from aiogram import Bot as AioBot
from aiogram.types import BotCommand
from olgram.models.models import Bot
from aiohttp import web
from asyncio import get_event_loop
import ssl
from olgram.settings import ServerSettings
from locales.locale import _
from .custom import CustomRequestHandler

import logging


logger = logging.getLogger(__name__)


def path_for_bot(bot: Bot) -> str:
    return "/" + str(bot.code)


def url_for_bot(bot: Bot) -> str:
    return f"https://{ServerSettings.hook_host()}:{ServerSettings.hook_port()}" + path_for_bot(bot)


async def register_token(bot: Bot) -> bool:
    """
    注册一个 token
    :param bot: token
    :return:
    """
    await unregister_token(bot.decrypted_token())

    a_bot = AioBot(bot.decrypted_token())
    certificate = None
    if ServerSettings.use_custom_cert():
        certificate = open(ServerSettings.public_path(), 'rb')

    res = await a_bot.set_webhook(url_for_bot(bot), certificate=certificate, drop_pending_updates=True,
                                  max_connections=10)
    # await a_bot.set_my_commands([
    #     BotCommand("/start", _("（重新）启动机器人")),
    #     BotCommand("/security_policy", _("隐私政策"))
    # ])
    # await a_bot.set_my_commands([
    #      BotCommand("", _("（重新）启动机器人")),
    #      BotCommand("", _("隐私政策"))
    #  ])
    #   建议禁止上面的/start和/security_policy,直接删除命令就可以
    #   若果有需要,去除上方的#号即可

    await a_bot.session.close()
    del a_bot
    return res


async def unregister_token(token: str):
    """
    注册一个 token
    :param token: token
    :return:
    """
    bot = AioBot(token)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    del bot


def main():
    loop = get_event_loop()

    app = web.Application()
    app.router.add_route('*', r"/{name}", CustomRequestHandler, name='webhook_handler')

    context = None
    if ServerSettings.use_custom_cert():
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(ServerSettings.public_path(), ServerSettings.priv_path())

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    logger.info("服务器初始化完成")
    site = web.TCPSite(runner, port=ServerSettings.app_port(), ssl_context=context)
    return site
