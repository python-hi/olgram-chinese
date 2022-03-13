"""
Здесь метрики
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
import socket
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

    bots = await models.Bot.all()
    bots_count = len(bots)
    user_count = len(await models.User.all())
    templates_count = len(await models.DefaultAnswer.all())

    income_messages = sum([bot.incoming_messages_count for bot in bots])
    outgoing_messages = sum([bot.outgoing_messages_count for bot in bots])

    hostname = socket.gethostname()

    await message.answer(f"Количество ботов: {bots_count}\n"
                         f"Количество пользователей (у конструктора): {user_count}\n"
                         f"Шаблонов ответов: {templates_count}\n"
                         f"Входящих сообщений у всех ботов: {income_messages}\n"
                         f"Исходящих сообщений у всех ботов: {outgoing_messages}\n"
                         f"Хост: {hostname}")
