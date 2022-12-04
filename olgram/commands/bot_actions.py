"""
这是使用特定机器人的工作
"""
from aiogram import types
from aiogram.utils.exceptions import TelegramAPIError, Unauthorized
from aiogram import Bot as AioBot
from olgram.models.models import Bot
from server.server import unregister_token
from locales.locale import _


async def delete_bot(bot: Bot, call: types.CallbackQuery):
    """
    用户决定删除机器人
    """
    try:
        await unregister_token(bot.decrypted_token())
    except Unauthorized:
        # 用户可能重置令牌或删除机器人，这些不再是我们的问题
        pass
    await bot.delete()
    await call.answer(_("删除机器人"))
    try:
        await call.message.delete()
    except TelegramAPIError:
        pass


async def reset_bot_text(bot: Bot, call: types.CallbackQuery):
    """
    用户决定将机器人的文本重置为默认值
    :param bot:
    :param call:
    :return:
    """
    bot.start_text = bot._meta.fields_map['start_text'].default
    await bot.save()
    await call.answer(_("重置文本"))


async def reset_bot_second_text(bot: Bot, call: types.CallbackQuery):
    """
    用户决定重置机器人的第二个文本
    :param bot:
    :param call:
    :return:
    """
    bot.second_text = bot._meta.fields_map['second_text'].default
    await bot.save()
    await call.answer(_("重置文本"))


async def select_chat(bot: Bot, call: types.CallbackQuery, chat: str):
    """
    用户选择了一个他想从机器人接收消息的群组
    :param bot:
    :param call:
    :param chat:
    :return:
    """
    if chat == "personal":
        bot.group_chat = None
        await bot.save()
        await call.answer(_("选择了私聊"))
        return
    if chat == "leave":
        bot.group_chat = None
        await bot.save()
        chats = await bot.group_chats.all()
        a_bot = AioBot(bot.decrypted_token())
        for chat in chats:
            try:
                await chat.delete()
                await a_bot.leave_chat(chat.chat_id)
            except TelegramAPIError:
                pass
        await call.answer(_("Бот вышел из чатов"))
        await a_bot.session.close()
        return

    chat_obj = await bot.group_chats.filter(id=chat).first()
    if not chat_obj:
        await call.answer(_("你不能将机器人链接到这个群聊"))
        return
    bot.group_chat = chat_obj
    await bot.save()
    await call.answer(_("聊天选择 {0}").format(chat_obj.name))


async def threads(bot: Bot, call: types.CallbackQuery):
    bot.enable_threads = not bot.enable_threads
    await bot.save(update_fields=["enable_threads"])


async def additional_info(bot: Bot, call: types.CallbackQuery):
    bot.enable_additional_info = not bot.enable_additional_info
    await bot.save(update_fields=["enable_additional_info"])


async def olgram_text(bot: Bot, call: types.CallbackQuery):
    if await bot.is_promo():
        bot.enable_olgram_text = not bot.enable_olgram_text
        await bot.save(update_fields=["enable_olgram_text"])


async def antiflood(bot: Bot, call: types.CallbackQuery):
    bot.enable_antiflood = not bot.enable_antiflood
    await bot.save(update_fields=["enable_antiflood"])
