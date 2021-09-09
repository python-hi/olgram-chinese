import asyncio
from tortoise import Tortoise

from olgram.router import dp
from olgram.settings import TORTOISE_ORM

import olgram.commands.bots  # noqa: F401
import olgram.commands.start  # noqa: F401
import olgram.commands.menu  # noqa: F401
import olgram.commands.bot_actions  # noqa: F401

from server.server import main as server_main


async def init_database():
    await Tortoise.init(config=TORTOISE_ORM)


def main():
    """
    Classic polling
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    # loop.create_task(dp.start_polling())
    loop.create_task(server_main().start())

    loop.run_forever()


if __name__ == '__main__':
    main()
