from aiogram import types, Bot as AioBot
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import Unauthorized, TelegramAPIError
import re
from textwrap import dedent

from ..utils.router import Router
from olgram.models.bot import Bot
from olgram.models.user import User

router = Router()
token_pattern = r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}'


@router.message_handler(commands=["my_bots"])
async def my_bots(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id)
    bots = await Bot.filter(owner=user)
    if not bots:
        await message.answer(dedent("""
        У вас нет добавленных ботов. 

        Отправьте команду /add_bot, чтобы добавить бот.
        """))
        return

    bots_str = "\n".join(["@" + bot.name for bot in bots])
    await message.answer(dedent(f"""
    Ваши боты:
    {bots_str}
    """))


@router.message_handler(commands=["add_bot"])
async def add_bot(message: types.Message, state: FSMContext):
    await message.answer("Окей, пришли тогда токен plz")
    await state.set_state("add_bot")


@router.message_handler(state="add_bot", content_types="text", regexp="^[^/].+")  # Not command
async def bot_added(message: types.Message, state: FSMContext):
    token = re.findall(token_pattern, message.text)

    async def on_invalid_token():
        await message.answer(dedent("""
        Это не токен бота. 

        Токен выглядит вот так: 123456789:AAAA-abc123_AbcdEFghijKLMnopqrstu12
        """))

    async def on_dummy_token():
        await message.answer(dedent("""
        Не удалось запустить этого бота: неверный токен
        """))

    async def on_unknown_error():
        await message.answer(dedent("""
        Не удалось запустить этого бота: непредвиденная ошибка
        """))

    if not token:
        return await on_invalid_token()

    token = token[0]

    try:
        test_bot = AioBot(token)
        test_bot_info = await test_bot.get_me()
    except ValueError:
        return await on_invalid_token()
    except Unauthorized:
        return await on_dummy_token()
    except TelegramAPIError:
        return await on_unknown_error()

    user, _ = await User.get_or_create(telegram_id=message.from_user.id)
    bot = Bot(token=token, owner=user, name=test_bot_info.username)
    await bot.save()

    await message.answer("Бот добавлен!")
