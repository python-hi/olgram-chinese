"""
Здесь работа с конкретным ботом
"""
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
# Пользователь выбрал чат - личные сообщения
select_bot_chat_personal = CallbackData('chat_select_personal', 'bot_id')


def check_bot_owner(handler):
    """
    Этот декоратор запрещает пользователям вызывать callback's (inline кнопки) для ботов, которыми они не владеют
    """
    async def wrapped(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
        bot_id = callback_data["bot_id"]
        bot = await Bot.get_or_none(id=bot_id)
        if not bot or (await bot.owner).telegram_id != call.from_user.id:
            await call.answer("У вас нет прав на этого бота", show_alert=True)
            return

        return await handler(bot, call, callback_data, state)
    return wrapped


@router.callback_query_handler(select_bot.filter(), state="*")
@check_bot_owner
async def select_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал бота для редактирования
    """
    await try_delete_message(call.message)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Текст",
                                               callback_data=bot_operation.new(bot_id=bot.id, operation="text")))
    keyboard.insert(types.InlineKeyboardButton(text="Чат",
                                               callback_data=bot_operation.new(bot_id=bot.id, operation="chat")))
    keyboard.insert(types.InlineKeyboardButton(text="Удалить бот",
                                               callback_data=bot_operation.new(bot_id=bot.id, operation="delete")))
    keyboard.insert(types.InlineKeyboardButton(text="<<Вернуться к списку ботов",
                                               callback_data=bot_operation.new(bot_id=bot.id, operation="back")))

    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    Управление ботом @{bot.name}.

    Если у вас возникли вопросы по настройке бота, то посмотрите нашу справку /help.
    """), reply_markup=keyboard)


@router.callback_query_handler(bot_operation.filter(operation="delete"), state="*")
@check_bot_owner
async def delete_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Кнопка "удалить" для бота
    """
    await bot.delete()
    await call.answer("Бот удалён")
    await try_delete_message(call.message)


@router.callback_query_handler(bot_operation.filter(operation="chat"), state="*")
@check_bot_owner
async def chats_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Кнопка "чаты" для бота
    """
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
                                                   callback_data=select_bot_chat.new(bot_id=bot.id, chat_id=chat.id)))
    keyboard.insert(types.InlineKeyboardButton(text="Личные сообщения",
                                               callback_data=select_bot_chat_personal.new(bot_id=bot.id)))
    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    В этом разделе вы можете привязать бота @{bot.name} к чату. 
    Выберите чат, куда бот будет пересылать сообщения. 
    """), reply_markup=keyboard)


@router.callback_query_handler(select_bot_chat.filter(), state="*")
@check_bot_owner
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


@router.callback_query_handler(select_bot_chat_personal.filter(), state="*")
@check_bot_owner
async def chat_selected_personal_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал личный чат для бота
    """
    bot.group_chat = None
    await bot.save()
    await call.answer(f"Выбран личный чат")


@router.callback_query_handler(bot_operation.filter(operation="text"), state="*")
@check_bot_owner
async def text_bot_callback(bot: Bot, call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Кнопка "текст" для бота
    """
    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    Текущий текст бота по кнопке start:
    
    {bot.start_text}
    """))
