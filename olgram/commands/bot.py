"""
Здесь работа с конкретным ботом
"""
from aiogram import types, Bot as AioBot
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from textwrap import dedent

from olgram.utils.mix import try_delete_message
from olgram.models.models import Bot, User

from olgram.router import dp

# Пользователь выбрал бота
select_bot = CallbackData('bot_select', 'bot_id')
# Пользователь выбрал, что хочет сделать со своим ботом
bot_operation = CallbackData('bot_operation', 'bot_id', 'operation')
# Пользователь выбрал чат
select_bot_chat = CallbackData('chat_select', 'bot_id', 'chat_id')
# Пользователь выбрал чат - личные сообщения
select_bot_chat_personal = CallbackData('chat_select_personal', 'bot_id')


async def delete_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Кнопка "удалить" для бота
    """
    await bot.delete()
    await call.answer("Бот удалён")
    await try_delete_message(call.message)




async def chat_selected_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал групповой чат для бота
    """
    chat_id = callback_data["chat_id"]
    chat = await bot.group_chats.filter(id=chat_id).first()
    if not chat:
        await call.answer("Нельзя привязать бота к этому чату")
        return
    bot.group_chat = chat
    await bot.save()
    await call.answer(f"Выбран чат {chat.name}")


async def chat_selected_personal_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал личный чат для бота
    """
    bot.group_chat = None
    await bot.save()
    await call.answer(f"Выбран личный чат")


async def text_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Кнопка "текст" для бота
    """
    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    Текущий текст бота по кнопке start:
    
    {bot.start_text}
    """))
