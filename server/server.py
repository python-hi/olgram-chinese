from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import SendMessage, WebhookRequestHandler
from olgram.models.models import Bot
from aiohttp import web
import asyncio
import aiohttp


from olgram.settings import ServerSettings


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
    a_bot = AioBot(bot.token)
    res = await a_bot.set_webhook(url_for_bot(bot))
    await a_bot.session.close()
    return res


async def unregister_token(token: str):
    """
    Удалить токен
    :param token: токен
    :return:
    """
    bot = AioBot(token)
    await bot.session.close()
    await bot.delete_webhook()


async def cmd_start(message, *args, **kwargs):
    return SendMessage(chat_id=message.chat.id, text=f'Hi from webhook, bot {message.via_bot}',
                       reply_to_message_id=message.message_id)


class CustomRequestHandler(WebhookRequestHandler):

    def __init__(self, *args, **kwargs):
        self._dispatcher = None
        super(CustomRequestHandler, self).__init__(*args, **kwargs)

    def _create_dispatcher(self):
        key = self.request.url.path[1:]

        bot = await Bot.filter(code=key).first()
        if not bot:
            return None

        dp = Dispatcher(AioBot(bot.token))

        dp.register_message_handler(cmd_start, commands=['start'])

        return dp

    def post(self):
        # TODO: refactor
        self._dispatcher = self._create_dispatcher()
        super(CustomRequestHandler, self).post()
        self._dispatcher = None

    def get_dispatcher(self):
        """
        Get Dispatcher instance from environment

        :return: :class:`aiogram.Dispatcher`
        """
        return self._dispatcher


def main():
    loop = asyncio.get_event_loop()

    app = web.Application()
    app.router.add_route('*', r"/{name}", CustomRequestHandler, name='webhook_handler')

    runner = aiohttp.web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = aiohttp.web.TCPSite(runner, host=ServerSettings.app_host(), port=ServerSettings.app_port())
    return site
