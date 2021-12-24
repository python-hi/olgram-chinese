"""
Здесь метрики
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from olgram.models import models

from olgram.router import dp
from olgram.settings import OlgramSettings


@dp.message_handler(commands=["info"], state="*")
async def info(message: types.Message, state: FSMContext):
    """
    Команда /info
    """

    if message.chat.id != OlgramSettings.supervisor_id():
        await message.answer("Недостаточно прав")
        return

    bots_count = len(await models.Bot.all())
    user_count = len(await models.User.all())

    await message.answer(f"Количество ботов: {bots_count}"
                         f"Количество пользователей: {user_count}")
