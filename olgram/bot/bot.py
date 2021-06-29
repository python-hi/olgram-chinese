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
bot_operation = CallbackData('bot_operation', 'operation')


@router.callback_query_handler(select_bot.filter())
async def select_bot_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Пользователь выбрал бота для редактирования
    """
    bot_id = callback_data["bot_id"]
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("Такого бота нет", show_alert=True)
        return

    async with state.proxy() as proxy:
        proxy["bot"] = bot

    await try_delete_message(call.message)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Текст", callback_data=bot_operation.new(operation="text")))
    keyboard.insert(types.InlineKeyboardButton(text="Чат", callback_data=bot_operation.new(operation="chat")))
    keyboard.insert(types.InlineKeyboardButton(text="Удалить бот", callback_data=bot_operation.new(operation="delete")))
    keyboard.insert(types.InlineKeyboardButton(text="<<Вернуться к списку ботов",
                                               callback_data=bot_operation.new(operation="back")))

    await AioBot.get_current().send_message(call.message.chat.id, dedent(f"""
    Управление ботом @{bot.name}.

    Если у вас возникли вопросы по настройке бота, то посмотрите нашу справку /help.
    """), reply_markup=keyboard)

