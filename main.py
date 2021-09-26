import asyncio
from tortoise import Tortoise

from olgram.router import dp
from olgram.settings import TORTOISE_ORM
from server.custom import init_redis

import olgram.commands.bots  # noqa: F401
import olgram.commands.start  # noqa: F401
import olgram.commands.menu  # noqa: F401
import olgram.commands.bot_actions  # noqa: F401

from server.server import main as server_main

import logging
logging.basicConfig(level=logging.INFO)


async def init_database():
    await Tortoise.init(config=TORTOISE_ORM)


async def init_olgram():
    from olgram.router import bot
    from aiogram.types import BotCommand
    await bot.set_my_commands(
        [
            BotCommand("start", "Запустить бота"),
            BotCommand("addbot", "Добавить бот"),
            BotCommand("mybots", "Управление ботами"),
            BotCommand("help", "Справка")
        ]
    )


async def initialization():
    await init_database()
    await init_redis()
    await init_olgram()


def main():
    """
    Classic polling
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialization())

    loop.create_task(dp.start_polling())
    # loop.create_task(server_main().start())

    loop.run_forever()


if __name__ == '__main__':
    main()
