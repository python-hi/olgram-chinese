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
    Olgram Bot — это конструктор ботов обратной связи в Telegram.

    Используйте эти команды, чтобы управлять этим ботом:

    /addbot - добавить бот
    /mybots - управление ботами

    /help - помощь

    Ссылка на репозиторий https://github.com/civsocit/olgram
    """))


@dp.message_handler(commands=["help"], state="*")
async def help(message: types.Message, state: FSMContext):
    """
    Команда /help
    """
    await message.answer(dedent(f"""
    О проекте https://telegra.ph/Olgram-09-15

    Поддержка: @civsocit_feedback_bot

    Версия {OlgramSettings.version()}
    """))
