from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import WebhookRequestHandler
from aiogram.dispatcher.webhook import SendMessage
from aiogram import types
from contextvars import ContextVar
from aiohttp.web_exceptions import HTTPNotFound
from olgram.models.models import Bot

db_bot_instance: ContextVar[Bot] = ContextVar('db_bot_instance')


async def message_handler(message, *args, **kwargs):
    if message.text and message.text.startswith("/start"):
        # На команду start нужно ответить, не пересылая сообщение никуда
        return SendMessage(chat_id=message.chat.id,
                           text=db_bot_instance.get().start_text)


class CustomRequestHandler(WebhookRequestHandler):

    def __init__(self, *args, **kwargs):
        self._dispatcher = None
        super(CustomRequestHandler, self).__init__(*args, **kwargs)

    async def _create_dispatcher(self):
        key = self.request.url.path[1:]

        bot = await Bot.filter(code=key).first()
        if not bot:
            return None
        db_bot_instance.set(bot)
        dp = Dispatcher(AioBot(bot.token))

        dp.register_message_handler(message_handler, content_types=[types.ContentType.TEXT,
                                                                    types.ContentType.CONTACT,
                                                                    types.ContentType.ANIMATION,
                                                                    types.ContentType.AUDIO,
                                                                    types.ContentType.DOCUMENT,
                                                                    types.ContentType.PHOTO,
                                                                    types.ContentType.STICKER,
                                                                    types.ContentType.VIDEO,
                                                                    types.ContentType.VOICE])

        return dp

    async def post(self):
        dispatcher = await self._create_dispatcher()
        if not dispatcher:
            raise HTTPNotFound()

        Dispatcher.set_current(dispatcher)
        AioBot.set_current(dispatcher.bot)
        return await super(CustomRequestHandler, self).post()

    def get_dispatcher(self):
        """
        Get Dispatcher instance from environment

        :return: :class:`aiogram.Dispatcher`
        """
        return Dispatcher.get_current()

