from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

from ..utils.router import Router

router = Router()


@router.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    """
    Start command handler
    """

    await message.answer(
        "Привет. Я бот Olgram"
    )
