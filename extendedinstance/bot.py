from aiogram import types
import asyncio
import aiocache
import typing as ty
from instance.bot import BotInstance, BotProperties
from olgram.models.models import Bot, GroupChat


class BotInstanceDatabase(BotInstance):
    _instances: ty.Dict[int, "BotInstanceDatabase"] = dict()

    def __init__(self, bot: Bot):
        self._bot = bot
        super().__init__()

    @classmethod
    async def run_all(cls):
        bots = await Bot.all()
        for bot in bots:
            cls._instances[bot.id] = BotInstanceDatabase(bot)
            # Polling только для отладки
            asyncio.get_event_loop().create_task(cls._instances[bot.id].start_polling())

    @aiocache.cached(ttl=5)
    async def _properties(self) -> BotProperties:
        await self._bot.refresh_from_db()
        return BotProperties(self._bot.token, self._bot.start_text, int(self._bot.token.split(":")[0]),
                             await self._bot.super_chat_id())

    async def _setup(self):
        await super()._setup()
        # Callback-и на добавление бота в чат и удаление бота из чата
        self._dp.register_message_handler(self._receive_invite, content_types=[types.ContentType.NEW_CHAT_MEMBERS])
        self._dp.register_message_handler(self._receive_left, content_types=[types.ContentType.LEFT_CHAT_MEMBER])

    async def _receive_invite(self, message: types.Message):
        for member in message.new_chat_members:
            if member.id == message.bot.id:
                chat, _ = await GroupChat.get_or_create(chat_id=message.chat.id,
                                                        defaults={"name": message.chat.full_name})
                if chat not in await self._bot.group_chats.all():
                    await self._bot.group_chats.add(chat)
                    await self._bot.save()
                break

    async def _receive_left(self, message: types.Message):
        if message.left_chat_member.id == message.bot.id:
            chat = await self._bot.group_chats.filter(chat_id=message.chat.id).first()
            if chat:
                await self._bot.group_chats.remove(chat)
                if self._bot.group_chat == chat:
                    self._bot.group_chat = None
                    await self._bot.save(update_fields=["group_chat"])
