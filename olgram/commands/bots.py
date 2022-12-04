"""
Здесь работа с ботами на первом уровне вложенности: список ботов, добавление ботов
"""
from aiogram import types, Bot as AioBot
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import Unauthorized, TelegramAPIError
from tortoise.exceptions import IntegrityError
import re
from textwrap import dedent

from olgram.models.models import Bot, User
from olgram.settings import OlgramSettings, BotSettings
from olgram.commands.menu import send_bots_menu
from server.server import register_token
from locales.locale import _

from olgram.router import dp

import logging

logger = logging.getLogger(__name__)


token_pattern = r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}'


@dp.message_handler(commands=["mybots"], state="*")
async def my_bots(message: types.Message, state: FSMContext):
    """
    命令 /mybots （机器人列表）
    """
    return await send_bots_menu(message.chat.id, message.from_user.id)


@dp.message_handler(commands=["addbot"], state="*")
async def add_bot(message: types.Message, state: FSMContext):
    """
    命令 /addbot（添加机器人）
    """
    user = await User.get_or_none(telegram_id=message.from_user.id)
    max_bot_count = OlgramSettings.max_bots_per_user()
    if user and await user.is_promo():
        max_bot_count = OlgramSettings.max_bots_per_user_promo()
    bot_count = await Bot.filter(owner__telegram_id=message.from_user.id).count()
    if bot_count >= max_bot_count:
        await message.answer(_("当前设置为每人只能创建10个转发机器人"))
        return

    await message.answer(dedent(_("""
    添加新的转发机器人

    1. 转到机器人 @BotFather，按 /start 键后,发送 /newbot
    2. 输入机器人的名字，然后输入机器人的用户名 @***bot
    3. 创建机器人后，将机器人的API Token发给我

    重要：不要连接其他转发机器人（Manybot、Chatfuel、Livegram等）
    """)))
    await state.set_state("add_bot")


@dp.message_handler(state="add_bot", content_types="text", regexp="^[^/].+")  # Not command
async def bot_added(message: types.Message, state: FSMContext):
    """
    添加一个机器人，请提供一个 token
    """
    token = re.findall(token_pattern, message.text)

    async def on_invalid_token():
        await message.answer(dedent(_("""
        机器人token错误,格式不正确
        """)))

    async def on_dummy_token():
        await message.answer(dedent(_("""
        添加机器人失败：错误的令牌
        """)))

    async def on_unknown_error():
        await message.answer(dedent(_("""
        机器人无法启动：意外错误
        """)))

    async def on_duplication_bot():
        await message.answer(dedent(_("""
        已存在的机器人
        """)))

    if not token:
        return await on_invalid_token()

    token = token[0]

    try:
        test_bot = AioBot(token)
        test_bot_info = await test_bot.get_me()
        await test_bot.session.close()
    except ValueError:
        return await on_invalid_token()
    except Unauthorized:
        return await on_dummy_token()
    except TelegramAPIError:
        return await on_unknown_error()

    if token == BotSettings.token():
        return await on_duplication_bot()

    user, created = await User.get_or_create(telegram_id=message.from_user.id)
    bot = Bot(token=Bot.encrypted_token(token), owner=user, name=test_bot_info.username,
              super_chat_id=message.from_user.id)
    try:
        await bot.save()
    except IntegrityError:
        return await on_duplication_bot()

    if not await register_token(bot):
        await bot.delete()
        return await on_unknown_error()

    await message.answer(_("添加成功! 机器人列表：/mybots "))
    await state.reset_state()
