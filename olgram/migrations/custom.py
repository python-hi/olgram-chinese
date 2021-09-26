"""Наши собственные миграции, которые нельзя описать на языке SQL и с которыми не справится TortoiseORM/Aerich"""

from tortoise import transactions, Tortoise
from olgram.settings import TORTOISE_ORM
from olgram.models.models import MetaInfo, Bot
import logging


async def upgrade_1():
    """Шифруем токены"""
    meta_info = await MetaInfo.first()
    if meta_info.version != 0:
        logging.info("skip")
        return

    async with transactions.in_transaction():
        bots = await Bot.all()
        for bot in bots:
            bot.token = bot.encrypted_token(bot.token)
            await bot.save()
        meta_info.version = 1
        await meta_info.save()
    logging.info("done")

# Не забудь добавить миграцию в этот лист!
_migrations = [upgrade_1]


async def migrate():
    logging.info("Run custom migrations...")
    await Tortoise.init(config=TORTOISE_ORM)

    for migration in _migrations:
        logging.info(f"Migration {migration.__name__}...")
        await migration()
