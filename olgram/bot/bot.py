from aiogram import types, Bot as AioBot
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from textwrap import dedent

from olgram.utils.router import Router
from olgram.utils.mix import try_delete_message
from olgram.models.models import Bot, User

router = Router()

# Пользователь выбрал бота
select_bot = CallbackData('bot_select', 'bot_id')
# Пользователь выбрал, что хочет сделать со своим ботом
bot_operation = CallbackData('bot_operation', 'bot_id', 'operation')
# Пользователь выбрал чат
select_bot_chat = CallbackData('chat_select', 'bot_id', 'chat_id')


@router.callback_query_handler(select_bot.filter(), state="*")
async def select_bot_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал бота для редактирования
    """
    bot_id = callback_data["bot_id"]
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("Такого бота нет, либо он принадлежит не вам", show_alert=True)
        return

    await try_delete_message(call.message)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Текст",
                                               callback_data=bot_operation.new(bot_id=bot_id, operation="text")))
    keyboard.insert(types.InlineKeyboardButton(text="Чат",
                                               callback_data=bot_operation.new(bot_id=bot_id, operation="chat")))
    keyboard.insert(types.InlineKeyboardButton(text="Удалить бот",
                                               callback_data=bot_operation.new(bot_id=bot_id, operation="delete")))
    keyboard.insert(types.InlineKeyboardButton(text="<<Вернуться к списку ботов",
                                               callback_data=bot_operation.new(bot_id=bot_id, operation="back")))

    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    Управление ботом @{bot.name}.

    Если у вас возникли вопросы по настройке бота, то посмотрите нашу справку /help.
    """), reply_markup=keyboard)


@router.callback_query_handler(bot_operation.filter(operation="delete"), state="*")
async def delete_bot_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    bot_id = callback_data["bot_id"]
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("Такого бота нет, либо он принадлежит не вам", show_alert=True)
        return

    await bot.delete()
    await call.answer("Бот удалён")
    await try_delete_message(call.message)


@router.callback_query_handler(bot_operation.filter(operation="chat"), state="*")
async def chats_bot_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    bot_id = callback_data["bot_id"]
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("Такого бота нет, либо он принадлежит не вам", show_alert=True)
        return

    await try_delete_message(call.message)

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    chats = await bot.group_chats.all()

    if not chats:
        return await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
        Этот бот не добавлен в чаты, поэтому все сообщения будут приходить вам в бот.
        Чтобы подключить чат — просто добавьте бот @{bot.name} в чат.
        """), reply_markup=keyboard)

    for chat in chats:
        keyboard.insert(types.InlineKeyboardButton(text=chat.name,
                                                   callback_data=select_bot_chat.new(bot_id=bot_id, chat_id=chat.id)))

    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    В этом разделе вы можете привязать бота @{bot.name} к чату. 
    Выберите чат, куда бот будет пересылать сообщения. 
    """), reply_markup=keyboard)
