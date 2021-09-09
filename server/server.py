from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import SendMessage, WebhookRequestHandler
from olgram.models.models import Bot
from aiohttp import web
import asyncio
import aiohttp
from olgram.settings import ServerSettings
import logging
logger = logging.getLogger(__name__)


def path_for_bot(bot: Bot) -> str:
    return "/" + bot.code


def url_for_bot(bot: Bot) -> str:
    return f"https://{ServerSettings.hook_host()}:{ServerSettings.hook_port()}" + path_for_bot(bot)


async def register_token(bot: Bot) -> bool:
    """
    Зарегистрировать токен
    :param bot: Бот
    :return: получилось ли
    """
    await unregister_token(bot.token)

    logger.info(f"register token {bot.name}")
    a_bot = AioBot(bot.token)
    res = await a_bot.set_webhook(url_for_bot(bot))
    del a_bot
    return res


async def unregister_token(token: str):
    """
    Удалить токен
    :param token: токен
    :return:
    """
    logger.info(f"unregister token {token}")
    bot = AioBot(token)
    await bot.delete_webhook()
    del bot


async def cmd_start(message, *args, **kwargs):
    logger.info("cmd start")
    return SendMessage(chat_id=message.chat.id, text=f'Hi from webhook, bot {message.via_bot}',
                       reply_to_message_id=message.message_id)


class CustomRequestHandler(WebhookRequestHandler):

    def __init__(self, *args, **kwargs):
        self._dispatcher = None
        super(CustomRequestHandler, self).__init__(*args, **kwargs)

    async def _create_dispatcher(self):
        key = self.request.url.path[1:]

        logger.info(f"create dispatcher {key}")

        bot = await Bot.filter(code=key).first()
        if not bot:
            return None

        dp = Dispatcher(AioBot(bot.token))

        dp.register_message_handler(cmd_start, commands=['start'])

        return dp

    async def post(self):
        # TODO: refactor
        logger.info(f"post request {self.request.url.path}")
        self._dispatcher = await self._create_dispatcher()
        res = await super(CustomRequestHandler, self).post()
        self._dispatcher = None
        return res

    def get_dispatcher(self):
        """
        Get Dispatcher instance from environment

        :return: :class:`aiogram.Dispatcher`
        """
        logger.info("get dispatcher")
        return self._dispatcher


def main():
    loop = asyncio.get_event_loop()

    app = web.Application()
    app.router.add_route('*', r"/{name}", CustomRequestHandler, name='webhook_handler')

    runner = aiohttp.web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    logger.info("server initialization done")
    site = aiohttp.web.TCPSite(runner, host=ServerSettings.app_host(), port=ServerSettings.app_port())
    return site
