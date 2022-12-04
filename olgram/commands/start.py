"""
Здесь простые команды на первом уровне вложенности: /start /help
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from textwrap import dedent
from olgram.settings import OlgramSettings
from olgram.utils.permissions import public
from locales.locale import _

from olgram.router import dp


@dp.message_handler(commands=["start"], state="*")
@public()
async def start(message: types.Message, state: FSMContext):
    """
    命令 /start
    """
    await state.reset_state()

    await message.answer(dedent(_("""\n
    创建telegram转发机器人

    使用这些命令来控制这个机器人:

    /addbot - 添加机器人
    /mybots - 我的机器人

    /help - 帮助
    """)), parse_mode="html", disable_web_page_preview=True)


@dp.message_handler(commands=["help"], state="*")
@public()
async def help(message: types.Message, state: FSMContext):
    """
    命令 /help
    """
    await message.answer(dedent(_("""
    这是一个自用型机器人,没有帮助信息.有问题我会自己解决
    如果有问题，请联系推广你使用的那个人
    """)).format(OlgramSettings.version()))


@dp.message_handler(commands=["chatid"], state="*")
@public()
async def chat_id(message: types.Message, state: FSMContext):
    """
    命令 /chatid
    """
    await message.answer(message.chat.id)
