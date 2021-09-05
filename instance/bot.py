import asyncio
import aiogram
import aioredis
from abc import ABC, abstractmethod
from dataclasses import dataclass
from aiogram import Dispatcher, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage

try:
    from settings import InstanceSettings
except ModuleNotFoundError:
    from .settings import InstanceSettings


@dataclass()
class BotProperties:
    token: str
    start_text: str
    bot_id: int
    super_chat_id: int


class BotInstance(ABC):
    def __init__(self):
        self._redis: aioredis.Redis = None
        self._dp: aiogram.Dispatcher = None

    @abstractmethod
    async def _properties(self) -> BotProperties:
        raise NotImplemented()

    def stop_polling(self):
        print("stop polling")
        self._dp.stop_polling()

    async def _setup(self):
        self._redis = await aioredis.create_redis_pool(InstanceSettings.redis_path())

        props = await self._properties()

        bot = aiogram.Bot(props.token)
        self._dp = Dispatcher(bot, storage=MemoryStorage())

        # Здесь перечислены все типы сообщений, которые бот должен пересылать
        self._dp.register_message_handler(self._receive_message, content_types=[types.ContentType.TEXT,
                                                                                types.ContentType.CONTACT,
                                                                                types.ContentType.ANIMATION,
                                                                                types.ContentType.AUDIO,
                                                                                types.ContentType.DOCUMENT,
                                                                                types.ContentType.PHOTO,
                                                                                types.ContentType.STICKER,
                                                                                types.ContentType.VIDEO,
                                                                                types.ContentType.VOICE])

    async def start_polling(self):
        print("start polling")
        await self._setup()
        await self._dp.start_polling()

    @classmethod
    def _message_unique_id(cls, bot_id: int, message_id: int) -> str:
        return f"{bot_id}_{message_id}"

    async def _receive_message(self, message: types.Message):
        """
        Получено обычное сообщение, вероятно, для пересыла в другой чат
        :param message:
        :return:
        """
        props = await self._properties()
        if message.text and message.text.startswith("/start"):
            # На команду start нужно ответить, не пересылая сообщение никуда
            await message.answer(props.start_text)
            return

        if message.chat.id != props.super_chat_id:
            # Это обычный чат: сообщение нужно переслать в супер-чат
            new_message = await message.forward(props.super_chat_id)
            await self._redis.set(self._message_unique_id(props.bot_id, new_message.message_id),
                                  message.chat.id)
        else:
            # Это супер-чат
            if message.reply_to_message:
                # Ответ из супер-чата переслать тому пользователю,
                chat_id = await self._redis.get(
                    self._message_unique_id(props.bot_id, message.reply_to_message.message_id))
                if not chat_id:
                    chat_id = message.reply_to_message.forward_from_chat
                    if not chat_id:
                        await message.reply("Невозможно переслать сообщение: автор не найден")
                        return
                chat_id = int(chat_id)
                try:
                    await message.copy_to(chat_id)
                except exceptions.MessageError:
                    await message.reply("Невозможно переслать сообщение: возможно, автор заблокировал бота")
                    return
            else:
                await message.forward(props.super_chat_id)


class FreezeBotInstance(BotInstance):
    def __init__(self, token: str, start_text: str, super_chat_id: int):
        super().__init__()

        self._props = BotProperties(token, start_text, int(token.split(":")[0]), super_chat_id)

    async def _properties(self) -> BotProperties:
        return self._props


if __name__ == '__main__':
    """
    Режим single-instance. В этом режиме не работает olgram. На сервере запускается только один feedback (instance)
    бот для пересылки сообщений. Все настройки этого бота задаются в переменных окружения на сервере. Бот работает 
    в режиме polling
    """
    bot = FreezeBotInstance(
        InstanceSettings.token(),
        InstanceSettings.start_text(),
        InstanceSettings.super_chat_id()
    )
    asyncio.get_event_loop().run_until_complete(bot.start_polling())
