import asyncio

import aiogram.types
from aiogram import Bot as AioBot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from olgram.settings import BotSettings

from olgram.bot.bots import router as bots_router
from olgram.bot.start import router as start_router
from olgram.bot.bot import router as bot_router
from olgram.utils.database import init_database

from olgram.models.models import Bot, GroupChat

from instance.bot import BotInstance

import typing as ty


async def invite_callback(identify: int, message: aiogram.types.Message):
    bot = await Bot.get(id=identify)
    chat, _ = await GroupChat.get_or_create(chat_id=message.chat.id,
                                            defaults={"name": message.chat.full_name})
    if chat not in await bot.group_chats.all():
        await bot.group_chats.add(chat)


async def left_callback(identify: int, message: aiogram.types.Message):
    bot = await Bot.get(id=identify)

    chat = await bot.group_chats.get_or_none(chat_id=message.chat.id)
    if chat:
        await bot.group_chats.remove(chat)


def run_bot(bot: BotInstance, loop: ty.Optional[asyncio.AbstractEventLoop] = None):
    loop = loop or asyncio.get_event_loop()
    loop.create_task(bot.start_polling())


async def run_all_bots(loop: asyncio.AbstractEventLoop):
    bots = await Bot.all()
    for bot in bots:
        run_bot(BotInstance(bot.token,
                            bot.super_chat_id,
                            bot.start_text,
                            invite_callback=invite_callback,
                            left_callback=left_callback,
                            identify=bot.id), loop)


def main():
    """
    Classic polling
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    bot = AioBot(BotSettings.token())
    dp = Dispatcher(bot, storage=MemoryStorage())

    start_router.setup(dp)
    bots_router.setup(dp)
    bot_router.setup(dp)

    loop.run_until_complete(run_all_bots(loop))
    loop.create_task(dp.start_polling())

    loop.run_forever()


if __name__ == '__main__':
    main()
