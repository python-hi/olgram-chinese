import asyncio
from tortoise import Tortoise

from olgram.router import dp
from olgram.settings import TORTOISE_ORM

import olgram.commands.bot
import olgram.commands.bots
import olgram.commands.start
import olgram.commands.menu


async def init_database():
    await Tortoise.init(config=TORTOISE_ORM)


def main():
    """
    Classic polling
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    loop.create_task(dp.start_polling())

    loop.run_forever()


if __name__ == '__main__':
    main()
