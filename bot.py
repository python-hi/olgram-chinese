import asyncio
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import BotSettings

from olgram.bot.bots import router as bots_router
from olgram.bot.start import router as start_router

from olgram.utils.database import init_database


def main():
    """
    Classic polling
    """
    asyncio.get_event_loop().run_until_complete(init_database())

    bot = Bot(BotSettings.token())
    dp = Dispatcher(bot, storage=MemoryStorage())

    start_router.setup(dp)
    bots_router.setup(dp)

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
