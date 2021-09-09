from olgram.router import dp

from aiogram import types, Bot as AioBot
from olgram.models.models import Bot, User
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from textwrap import dedent
from olgram.utils.mix import edit_or_create
from olgram.commands import bot_actions

import typing as ty


menu_callback = CallbackData('menu', 'level', 'bot_id', 'operation', 'chat')

empty = "0"


async def send_bots_menu(chat_id: int, user_id: int, call=None):
    """
    Отправить пользователю список ботов
    :return:
    """
    if call:
        await call.answer()

    user = await User.get_or_none(telegram_id=user_id)
    bots = await Bot.filter(owner=user)
    if not bots:
        await AioBot.get_current().send_message(chat_id, dedent("""
        У вас нет добавленных ботов.

        Отправьте команду /addbot, чтобы добавить бот.
        """))
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for bot in bots:
        keyboard.insert(
            types.InlineKeyboardButton(text="@" + bot.name,
                                       callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                       chat=empty))
        )

    text = "Ваши боты"
    if call:
        await edit_or_create(call, text, keyboard)
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard)


async def send_chats_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    chats = await bot.group_chats.all()

    for chat in chats:
        keyboard.insert(
            types.InlineKeyboardButton(text=chat.name,
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat=chat.id))
        )
    if chats:
        keyboard.insert(
            types.InlineKeyboardButton(text="Личные сообщения",
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat="personal"))
        )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                   chat=empty))
    )

    if not chats:
        text = dedent(f"""
        Этот бот не добавлен в чаты, поэтому все сообщения будут приходить вам в бот.
        Чтобы подключить чат — просто добавьте бот @{bot.name} в чат.
        """)
    else:
        text = dedent(f"""
        В этом разделе вы можете привязать бота @{bot.name} к чату.
        Выберите чат, куда бот будет пересылать сообщения.
        """)

    await edit_or_create(call, text, keyboard)


async def send_bot_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="Текст",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Чат",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="chat",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Удалить бот",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="delete",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=0, bot_id=empty, operation=empty, chat=empty))
    )

    await edit_or_create(call, dedent(f"""
    Управление ботом @{bot.name}.

    Если у вас возникли вопросы по настройке бота, то посмотрите нашу справку /help.
    """), reply_markup=keyboard)


async def send_bot_delete_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="Да, удалить бот",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="delete_yes",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    await edit_or_create(call, dedent(f"""
    Вы уверены, что хотите удалить бота @{bot.name}?
    """), reply_markup=keyboard)


async def send_bot_text_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None, chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="Сбросить текст",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="reset_text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Завершить редактирование",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    text = dedent("""
    Сейчас вы редактируете текст, который отправляется после того, как пользователь отправит вашему боту
    команду /start

    Текущий текст:
    ```
    {0}
    ```
    Отправьте сообщение, чтобы изменить текст.
    """)
    text = text.format(bot.start_text)
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="markdown")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="markdown")


@dp.message_handler(state="wait_start_text", content_types="text", regexp="^[^/].+")  # Not command
async def start_text_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)
    bot.start_text = message.text
    await bot.save()
    await send_bot_text_menu(bot, chat_id=message.chat.id)


@dp.callback_query_handler(menu_callback.filter(), state="*")
async def callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    level = callback_data.get("level")

    if level == "0":
        return await send_bots_menu(call.message.chat.id, call.from_user.id, call)

    bot_id = callback_data.get("bot_id")
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("У вас нет прав на этого бота", show_alert=True)
        return

    if level == "1":
        return await send_bot_menu(bot, call)

    operation = callback_data.get("operation")
    if level == "2":
        await state.reset_state()
        if operation == "chat":
            return await send_chats_menu(bot, call)
        if operation == "delete":
            return await send_bot_delete_menu(bot, call)
        if operation == "text":
            await state.set_state("wait_start_text")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_text_menu(bot, call)

    if level == "3":
        if operation == "delete_yes":
            return await bot_actions.delete_bot(bot, call)
        if operation == "chat":
            return await bot_actions.select_chat(bot, call, callback_data.get("chat"))
        if operation == "reset_text":
            await bot_actions.reset_bot_text(bot, call)
            return await send_bot_text_menu(bot, call)
