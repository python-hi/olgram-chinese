from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import WebhookRequestHandler
from aiogram.dispatcher.webhook import SendMessage
from aiogram import types
from olgram.models.models import Bot


async def message_handler(message, *args, **kwargs):
    if message.text and message.text.startswith("/start"):
        # На команду start нужно ответить, не пересылая сообщение никуда
        bot = AioBot.get_current()
        return SendMessage(chat_id=message.chat.id, text=f'Hi from webhook {args} {kwargs} {bot}')


class CustomRequestHandler(WebhookRequestHandler):

    def __init__(self, *args, **kwargs):
        self._dispatcher = None
        super(CustomRequestHandler, self).__init__(*args, **kwargs)


    async def _create_dispatcher(self):
        key = self.request.url.path[1:]

        bot = await Bot.filter(code=key).first()
        if not bot:
            return None

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
        Dispatcher.set_current(dispatcher)
        AioBot.set_current(dispatcher.bot)
        return await super(CustomRequestHandler, self).post()

    def get_dispatcher(self):
        """
        Get Dispatcher instance from environment

        :return: :class:`aiogram.Dispatcher`
        """
        return Dispatcher.get_current()

