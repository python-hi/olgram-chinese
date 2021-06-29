import asyncio
import aioredis
import typing as ty
from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from olgram.utils.router import Router

token = "(token)"
bot_id = token.split(":")[0]
start_text = 'Здравствуйте! Напишите тут что-то'
super_chat_id = -1  # ID чата здесь

router = Router()
redis: ty.Optional[aioredis.Redis] = None


def message_unique_id(message_id) -> str:
    return bot_id + "-" + str(message_id)


@router.message_handler(content_types=[types.ContentType.ANY])
async def receive_text(message: types.Message):
    """
    Some text received
    :param message:
    :return:
    """
    if message.text and message.text.startswith("/start"):
        await message.answer(start_text)
        return

    if message.chat.id != super_chat_id:
        # Это обычный чат
        new_message = await message.forward(super_chat_id)
        await redis.set(message_unique_id(new_message.message_id), message.chat.id)
    else:
        # Это чат, в который бот должен пересылать сообщения
        if message.reply_to_message:
            chat_id = await redis.get(message_unique_id(message.reply_to_message.message_id))
            if not chat_id:
                chat_id = message.reply_to_message.forward_from_chat
                if not chat_id:
                    await message.reply("Невозможно ответить, автор сообщения не найден")
                    return
            chat_id = int(chat_id)
            try:
                await message.copy_to(chat_id)
            except exceptions.MessageError:
                await message.reply("Невозможно отправить сообщение пользователю: возможно, он заблокировал бота")
                return

        else:
            await message.forward(super_chat_id)


async def init_redis():
    global redis
    redis = await aioredis.create_redis_pool('redis://localhost:6370')


def main():
    """
    Classic polling
    """

    asyncio.get_event_loop().run_until_complete(init_redis())

    bot = Bot(token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    router.setup(dp)

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
