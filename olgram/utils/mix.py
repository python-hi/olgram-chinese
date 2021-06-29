from aiogram.types import Message
from aiogram.utils.exceptions import TelegramAPIError


async def try_delete_message(message: Message):
    try:
        await message.delete()
    except TelegramAPIError:
        pass
