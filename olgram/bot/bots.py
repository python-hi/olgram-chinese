from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

from ..utils.router import Router

router = Router()


@router.message_handler(commands=["my_bots"])
async def my_bots(message: types.Message, state: FSMContext):
    await message.answer("У тебя много ботов )")


@router.message_handler(commands=["add_bot"])
async def add_bot(message: types.Message, state: FSMContext):
    await message.answer("Добавь тогда ок")
