"""
Здесь простые команды на первом уровне вложенности: /start /help
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from textwrap import dedent
from olgram.settings import OlgramSettings

from olgram.router import dp


@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    """
    Команда /start
    """
    await state.reset_state()

    # TODO: locale

    await message.answer(dedent("""
    Olgram Bot — это конструктор ботов обратной связи в Telegram. Подробнее
    <a href="https://olgram.readthedocs.io">читайте здесь</a>

    Используйте эти команды, чтобы управлять этим ботом:

    /addbot - добавить бот
    /mybots - управление ботами

    /help - помощь
    """), parse_mode="html")


@dp.message_handler(commands=["help"], state="*")
async def help(message: types.Message, state: FSMContext):
    """
    Команда /help
    """
    await message.answer(dedent(f"""
    Читайте инструкции на нашем сайте https://olgram.readthedocs.io
    Техническая поддержка: @civsocit_feedback_bot
    Версия {OlgramSettings.version()}
    """))
