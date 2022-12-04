from aiogram import Bot as AioBot, Dispatcher
from aiogram.dispatcher.webhook import WebhookRequestHandler
from aiogram.dispatcher.webhook import SendMessage
from aiogram import exceptions
from aiogram import types
from contextvars import ContextVar
from aiohttp.web_exceptions import HTTPNotFound
from aioredis.commands import create_redis_pool
from aioredis import Redis
from tortoise.expressions import F
import logging
import typing as ty
from olgram.settings import ServerSettings
from olgram.models.models import Bot, GroupChat, BannedUser
from locales.locale import _, translators
from server.inlines import inline_handler

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

db_bot_instance: ContextVar[Bot] = ContextVar('db_bot_instance')

_redis: ty.Optional[Redis] = None


def _get_translator(message: types.Message) -> ty.Callable:
    if not message.from_user.locale:
        return _
    return translators.get(message.from_user.locale.language, _)


async def init_redis():
    global _redis
    _redis = await create_redis_pool(ServerSettings.redis_path())


def _message_unique_id(bot_id: int, message_id: int) -> str:
    return f"{bot_id}_{message_id}"


def _thread_uniqie_id(bot_id: int, chat_id: int) -> str:
    return f"thread_{bot_id}_{chat_id}"


def _last_message_uid(bot_id: int, chat_id: int) -> str:
    return f"lm_{bot_id}_{chat_id}"


def _antiflood_marker_uid(bot_id: int, chat_id: int) -> str:
    return f"af_{bot_id}_{chat_id}"


def _on_security_policy(message: types.Message, bot):
    _ = _get_translator(message)
    text = _("<b>隐私政策</b>\n\n"
             "该机器人不存储您的消息、用户名和@username。 \n"
             "当您发送消息时（除了 /start 和 /security_policy 命令），您的用户 ID 会被写入缓存一段时间，然后从缓存中删除。\n "
             "此标识符仅用于与操作员通信； 机器人不进行群发邮件。\n\n")
    if bot.enable_additional_info:
        text += _("发送消息时（ /start 和 /security_policy 命令除外），由于操作员在创建机器人时指定的设置，操作员会<b>看到</b>您的用户名、@username 和用户 ID。")
    else:
        text += _("根据telegram隐私设置，运营商可能会看到您的姓名，用户名和其他信息.")

    return SendMessage(chat_id=message.chat.id,
                       text=text,
                       parse_mode="HTML")


async def send_user_message(message: types.Message, super_chat_id: int, bot):
    """转发来自用户的消息，必要时添加用户信息"""
    if bot.enable_additional_info:
        user_info = _("")
        user_info += message.from_user.full_name
        if message.from_user.username:
            user_info += " | @" + message.from_user.username
        user_info += f" | #ID{message.from_user.id}"

        # 在文本末尾添加信息
        if message.content_type == types.ContentType.TEXT and len(message.text) + len(user_info) < 4093:  #我:E721
            new_message = await message.bot.send_message(super_chat_id, message.text + "\n\n" + user_info)
        else:  # 不要在正文末尾添加信息，信息在单独的消息中
            new_message = await message.bot.send_message(super_chat_id, text=user_info)
            new_message_2 = await message.copy_to(super_chat_id, reply_to_message_id=new_message.message_id)
            await _redis.set(_message_unique_id(bot.pk, new_message_2.message_id), message.chat.id,
                             pexpire=ServerSettings.redis_timeout_ms())
        await _redis.set(_message_unique_id(bot.pk, new_message.message_id), message.chat.id,
                         pexpire=ServerSettings.redis_timeout_ms())
        return new_message
    else:
        try:
            new_message = await message.forward(super_chat_id)
        except exceptions.MessageCantBeForwarded:
            new_message = await message.copy_to(super_chat_id)
        await _redis.set(_message_unique_id(bot.pk, new_message.message_id), message.chat.id,
                         pexpire=ServerSettings.redis_timeout_ms())
        return new_message


async def send_to_superchat(is_super_group: bool, message: types.Message, super_chat_id: int, bot):
    """将消息从用户转发给操作员（消息流逻辑）"""
    if is_super_group and bot.enable_threads:
        thread_first_message = await _redis.get(_thread_uniqie_id(bot.pk, message.chat.id))
        if thread_first_message:
            # 转发到超级聊天，回复上一条消息
            try:
                new_message = await message.copy_to(super_chat_id, reply_to_message_id=int(thread_first_message))
                await _redis.set(_message_unique_id(bot.pk, new_message.message_id), message.chat.id,
                                 pexpire=ServerSettings.redis_timeout_ms())
            except exceptions.BadRequest:
                new_message = await send_user_message(message, super_chat_id, bot)
                await _redis.set(_thread_uniqie_id(bot.pk, message.chat.id), new_message.message_id,
                                 pexpire=ServerSettings.thread_timeout_ms())
        else:
            # 转发超级聊天
            new_message = await send_user_message(message, super_chat_id, bot)
            await _redis.set(_thread_uniqie_id(bot.pk, message.chat.id), new_message.message_id,
                             pexpire=ServerSettings.thread_timeout_ms())
    else:  # 私信不支持消息流：简单转发
        await send_user_message(message, super_chat_id, bot)


async def handle_user_message(message: types.Message, super_chat_id: int, bot):
    """普通用户向机器人发送消息，您需要将其转发给运营商"""
    _ = _get_translator(message)
    is_super_group = super_chat_id < 0

    # 检查用户是否被禁止
    banned = await bot.banned_users.filter(telegram_id=message.chat.id)
    if banned:
        return SendMessage(chat_id=message.chat.id,
                           text=_("您在此机器人中被阻止"))

    # 检查防爆
    if bot.enable_antiflood:
        if await _redis.get(_antiflood_marker_uid(bot.pk, message.chat.id)):
            return SendMessage(chat_id=message.chat.id,
                               text=_("消息太多，请勿刷屏"))
        await _redis.setex(_antiflood_marker_uid(bot.pk, message.chat.id), 60, 1)

    # 将消息转发到超级聊天
    try:
        await send_to_superchat(is_super_group, message, super_chat_id, bot)
    except (exceptions.Unauthorized, exceptions.ChatNotFound):
        return SendMessage(chat_id=message.chat.id, text=_("无法联系机器人所有者"))
    except exceptions.TelegramAPIError as err:
        _logger.error(f"(exception on forwarding) {err}")
        return

    bot.incoming_messages_count = F("incoming_messages_count") + 1
    await bot.save(update_fields=["incoming_messages_count"])

    # 如果指定，则向用户发送特殊文本
    if bot.second_text:
        send_auto = not await _redis.get(_last_message_uid(bot.pk, message.chat.id))
        await _redis.setex(_last_message_uid(bot.pk, message.chat.id), 60 * 60 * 3, 1)
        if send_auto:
            return SendMessage(chat_id=message.chat.id, text=bot.second_text, parse_mode="HTML")


async def handle_operator_message(message: types.Message, super_chat_id: int, bot):
    """运营商写了一些东西，你需要将消息转发给用户，或者禁止他等。"""
    _ = _get_translator(message)

    if message.reply_to_message:

        if message.reply_to_message.from_user.id != message.bot.id:
            return  # 我们只对机器人消息的回复感兴趣

        # 在超级聊天中，有人回复了用户的消息，你需要转发给那个用户
        chat_id = await _redis.get(_message_unique_id(bot.pk, message.reply_to_message.message_id))
        if not chat_id:
            chat_id = message.reply_to_message.forward_from_chat
            if not chat_id:
                return SendMessage(chat_id=message.chat.id,
                                   text=_("<i>无法转发消息：找不到用户（消息太旧？）</i>"),
                                   parse_mode="HTML")
        chat_id = int(chat_id)

        if message.text == "/ban":
            user, create = await BannedUser.get_or_create(telegram_id=chat_id, bot=bot)
            await user.save()
            return SendMessage(chat_id=message.chat.id, text=_("用户已被屏蔽"))

        if message.text == "/unban":
            banned_user = await bot.banned_users.filter(telegram_id=chat_id).first()
            if not banned_user:
                return SendMessage(chat_id=message.chat.id, text=_("取消屏蔽"))
            else:
                await banned_user.delete()
                return SendMessage(chat_id=message.chat.id, text=_("用户解禁"))

        try:
            await message.copy_to(chat_id)
        except (exceptions.MessageError, exceptions.Unauthorized):
            await message.reply(_("<i>无法转发消息（机器人已被阻止？）</i>"),
                                parse_mode="HTML")
            return

        bot.outgoing_messages_count = F("outgoing_messages_count") + 1
        await bot.save(update_fields=["outgoing_messages_count"])

    elif super_chat_id > 0:
        # 在超级聊天中，有人给自己写了一条消息，仅用于私人消息
        await message.forward(super_chat_id)
        # 如果指定，则向用户发送特殊文本
        if bot.second_text:
            return SendMessage(chat_id=message.chat.id, text=bot.second_text, parse_mode="HTML")


async def message_handler(message: types.Message, *args, **kwargs):
    _ = _get_translator(message)
    bot = db_bot_instance.get()

    if message.text and message.text == "/start":
        # 必须在不将消息转发到任何地方的情况下回答启动命令
        text = bot.start_text
        if bot.enable_olgram_text:
            text += _(ServerSettings.append_text())
        return SendMessage(chat_id=message.chat.id, text=text, parse_mode="HTML")

    if message.text and message.text == "/security_policy":
        # 必须在不将消息转发到任何地方的情况下回答安全策略命令。
        return _on_security_policy(message, bot)

    super_chat_id = await bot.super_chat_id()

    if message.chat.id != super_chat_id:
        # Это обычный чат
        return await handle_user_message(message, super_chat_id, bot)
    else:
        # Это супер-чат
        return await handle_operator_message(message, super_chat_id, bot)


async def edited_message_handler(message: types.Message, *args, **kwargs):
    return await message_handler(message, *args, **kwargs, is_edited=True)


async def receive_invite(message: types.Message):
    bot = db_bot_instance.get()
    for member in message.new_chat_members:
        if member.id == message.bot.id:
            chat, _ = await GroupChat.get_or_create(chat_id=message.chat.id,
                                                    defaults={"name": message.chat.full_name})
            chat.name = message.chat.full_name
            await chat.save()
            if chat not in await bot.group_chats.all():
                await bot.group_chats.add(chat)
                await bot.save()
            break


async def receive_group_create(message: types.Message):
    bot = db_bot_instance.get()

    chat, _ = await GroupChat.get_or_create(chat_id=message.chat.id,
                                            defaults={"name": message.chat.full_name})
    chat.name = message.chat.full_name
    await chat.save()
    if chat not in await bot.group_chats.all():
        await bot.group_chats.add(chat)
        await bot.save()


async def receive_left(message: types.Message):
    bot = db_bot_instance.get()
    if message.left_chat_member.id == message.bot.id:
        chat = await bot.group_chats.filter(chat_id=message.chat.id).first()
        if chat:
            await bot.group_chats.remove(chat)
            bot_group_chat = await bot.group_chat
            if bot_group_chat == chat:
                bot.group_chat = None
            await bot.save()


async def receive_inline(inline_query):
    _logger.info("inline handler")
    bot = db_bot_instance.get()
    return await inline_handler(inline_query, bot)


async def receive_migrate(message: types.Message):
    bot = db_bot_instance.get()
    from_id = message.chat.id
    to_id = message.migrate_to_chat_id

    chats = await bot.group_chats.filter(chat_id=from_id)
    for chat in chats:
        chat.chat_id = to_id
        await chat.save(update_fields=["chat_id"])


class CustomRequestHandler(WebhookRequestHandler):

    def __init__(self, *args, **kwargs):
        self._dispatcher = None
        super(CustomRequestHandler, self).__init__(*args, **kwargs)

    async def _create_dispatcher(self):
        key = self.request.url.path[1:]

        bot = await Bot.filter(code=key).first()
        if not bot:
            return None
        db_bot_instance.set(bot)
        dp = Dispatcher(AioBot(bot.decrypted_token()))

        supported_messages = [types.ContentType.TEXT,
                              types.ContentType.CONTACT,
                              types.ContentType.ANIMATION,
                              types.ContentType.AUDIO,
                              types.ContentType.DOCUMENT,
                              types.ContentType.PHOTO,
                              types.ContentType.STICKER,
                              types.ContentType.VIDEO,
                              types.ContentType.VOICE,
                              types.ContentType.LOCATION]
        dp.register_message_handler(message_handler, content_types=supported_messages)
        dp.register_edited_message_handler(edited_message_handler, content_types=supported_messages)

        dp.register_message_handler(receive_invite, content_types=[types.ContentType.NEW_CHAT_MEMBERS])
        dp.register_message_handler(receive_left, content_types=[types.ContentType.LEFT_CHAT_MEMBER])
        dp.register_message_handler(receive_migrate, content_types=[types.ContentType.MIGRATE_TO_CHAT_ID])
        dp.register_message_handler(receive_group_create, content_types=[types.ContentType.GROUP_CHAT_CREATED])
        dp.register_inline_handler(receive_inline)

        return dp

    async def post(self):
        dispatcher = await self._create_dispatcher()
        if not dispatcher:
            raise HTTPNotFound()

        Dispatcher.set_current(dispatcher)
        AioBot.set_current(dispatcher.bot)
        return await super(CustomRequestHandler, self).post()

    def get_dispatcher(self):
        """
        Get Dispatcher instance from environment

        :return: :class:`aiogram.Dispatcher`
        """
        return Dispatcher.get_current()
