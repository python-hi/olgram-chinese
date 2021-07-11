import asyncio

from aiogram import Bot as AioBot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise.signals import post_delete, post_save
from tortoise import Tortoise

from olgram.settings import BotSettings, TORTOISE_ORM

from olgram.commands.bots import router as bots_router
from olgram.commands.start import router as start_router
from olgram.commands.bot import router as bot_router

from olgram.models.models import Bot
from extendedinstance.bot import BotInstanceDatabase


@post_save(Bot)
async def signal_post_save(
    sender,
    instance: Bot,
    created: bool,
    using_db,
    update_fields,
) -> None:
    if created:
        await BotInstanceDatabase.on_create(instance)


@post_delete(Bot)
async def signal_post_delete(sender, instance: Bot, using_db) -> None:
    await BotInstanceDatabase.on_delete(instance)


async def init_database():
    await Tortoise.init(config=TORTOISE_ORM)


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

    loop.run_until_complete(BotInstanceDatabase.run_all())
    loop.create_task(dp.start_polling())

    loop.run_forever()


if __name__ == '__main__':
    main()
