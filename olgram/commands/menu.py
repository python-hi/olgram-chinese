from olgram.router import dp

from aiogram import types, Bot as AioBot
from olgram.models.models import Bot, User, DefaultAnswer
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from textwrap import dedent
from olgram.utils.mix import edit_or_create, button_text_limit, wrap
from olgram.commands import bot_actions
from locales.locale import _

import typing as ty


menu_callback = CallbackData('menu', 'level', 'bot_id', 'operation', 'chat')

empty = "0"


async def send_bots_menu(chat_id: int, user_id: int, call=None):
    """
    向用户发送机器人列表
    :return:
    """
    if call:
        await call.answer()

    user = await User.get_or_none(telegram_id=user_id)
    bots = await Bot.filter(owner=user)
    if not bots:
        await AioBot.get_current().send_message(chat_id, dedent(_("""
        您没有添加任何机器人。

        发送 /addbot 命令以添加机器人。
        """)))
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for bot in bots:
        keyboard.insert(
            types.InlineKeyboardButton(text="@" + bot.name,
                                       callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                       chat=empty))
        )

    text = _("你的机器人")
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
            types.InlineKeyboardButton(text=button_text_limit(chat.name),
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat=chat.id))
        )
    if chats:
        keyboard.insert(
            types.InlineKeyboardButton(text=_("私人信息"),
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat="personal"))
        )
        keyboard.insert(
            types.InlineKeyboardButton(text=_("❗️ 退出所有聊天"),
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat="leave"))
        )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                   chat=empty))
    )

    if not chats:
        text = dedent(_("""
        这个机器人没有被添加群组，所有的消息都会转发到机器人
        将机器人 @{0} 添加到群组，再次打开此菜单并选择添加的群聊
        如果你的机器人在添加到转发机器人之前是在群组中，请将其从群聊中删除，然后添加到群组中
        """)).format(bot.name)
    else:
        text = dedent(_("""
        您可以将 @{0} 机器人绑定到一个群组中
        请问将机器人消息转发到哪个群组
        """)).format(bot.name)

    await edit_or_create(call, text, keyboard)


async def send_bot_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("自动回复"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("群组管理"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="chat",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("删除机器人"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="delete",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("统计数据"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="stat",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("返回"),
                                   callback_data=menu_callback.new(level=0, bot_id=empty, operation=empty, chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("其他功能"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="settings",
                                                                   chat=empty))
    )

    await edit_or_create(call, dedent(_("""
    机器人管理 @{0} 
    """)).format(bot.name), reply_markup=keyboard)


async def send_bot_delete_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("是的，删除机器人"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="delete_yes",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    await edit_or_create(call, dedent(_("""
    您确定要删除机器人吗 @{0}?
    """)).format(bot.name), reply_markup=keyboard)


async def send_bot_settings_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("消息流"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="threads",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("用户数据"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="additional_info",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("防爆"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="antiflood",
                                                                   chat=empty))
    )
    is_promo = await bot.is_promo()
    if is_promo:
        keyboard.insert(
            types.InlineKeyboardButton(text=_("机器人 签名"),
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="olgram_text",
                                                                       chat=empty))
        )

    keyboard.insert(
        types.InlineKeyboardButton(text=_("返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                   chat=empty))
    )

    thread_turn = _("开启") if bot.enable_threads else _("关闭")
    info_turn = _("开启") if bot.enable_additional_info else _("关闭")
    antiflood_turn = _("开启") if bot.enable_antiflood else _("关闭")
    text = dedent(_("""
    <a href="https://olgram.readthedocs.io/ru/latest/options.html#threads">消息流</a>: <b>{0}</b>
    <a href="https://olgram.readthedocs.io/ru/latest/options.html#user-info">用户数据</a>: <b>{1}</b>
    <a href="https://olgram.readthedocs.io/ru/latest/options.html#antiflood">防爆</a>: <b>{2}</b>
    """)).format(thread_turn, info_turn, antiflood_turn)

    if is_promo:
        olgram_turn = _("开启") if bot.enable_olgram_text else _("关闭")
        text += _("机器人 签名: <b>{0}</b>").format(olgram_turn)

    await edit_or_create(call, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_text_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None, chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("<< 保存并返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("自动回复"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="next_text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("重置文本"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="reset_text",
                                                                   chat=empty))
    )

    text = dedent(_("""
    向你的机器人 @{0} 发送 /start 之后的回复文本
    目前的文本
    -----------------------------------------------------------
    <pre>
    {1}
    </pre>
    
    -----------------------------------------------------------
    发送消息，改变文本
    """))
    text = text.format(bot.name, bot.start_text)
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_statistic_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None,
                                  chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    text = dedent(_("""
    机器人统计 @{0}

    收到的信息: <b>{1}</b>
    回复消息: <b>{2}</b>
    回复模板: <b>{3}</b>
    被禁止的用户: <b>{4}</b>
    """)).format(bot.name, bot.incoming_messages_count, bot.outgoing_messages_count, len(await bot.answers),
                 len(await bot.banned_users))
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_second_text_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None,
                                    chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("<< 保存并返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("以前的文本"),
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("回复模板..."),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="templates",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text=_("重置文本"),
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id,
                                                                   operation="reset_second_text", chat=empty))
    )

    text = dedent(_("""
    你现在正在编辑自动回复的文本。 @{0} 自动回复所有收到的信息
    默认情况下，它是禁用的
    目前的文本
    --------------------------------
    <pre>
    {1}
    </pre>
    
    --------------------------------
    发送消息，改变文本
    """))
    text = text.format(bot.name, bot.second_text if bot.second_text else _("(关闭)"))
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_templates_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None,
                                  chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text=_("<< 保存并返回"),
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    text = dedent(_("""
    你现在正在编辑 @{0} 的回复模板。目前的模板。

    <pre>
    {1}
    </pre>
    发送一些短语（例如：“您的订单已准备好，请稍候！”）将其添加到模板中。
    要从列表中删除模板，请发送其在列表中的编号（例如，4）
    """))

    templates = await bot.answers

    total_text_len = sum(len(t.text) for t in templates) + len(text)  # 近似文本长度
    max_len = 1000
    if total_text_len > 4000:
        max_len = 100

    templates_text = "\n".join(f"{n}. {wrap(template.text, max_len)}" for n, template in enumerate(templates))
    if not templates_text:
        templates_text = _("(没有模板)")
    text = text.format(bot.name, templates_text)
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


@dp.message_handler(state="wait_start_text", content_types="text", regexp="^[^/].+")  # Not command
async def start_text_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)
    bot.start_text = message.html_text
    await bot.save()
    await send_bot_text_menu(bot, chat_id=message.chat.id)


@dp.message_handler(state="wait_second_text", content_types="text", regexp="^[^/].+")  # Not command
async def second_text_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)
    bot.second_text = message.html_text
    await bot.save()
    await send_bot_second_text_menu(bot, chat_id=message.chat.id)


@dp.message_handler(state="wait_template", content_types="text", regexp="^[^/](.+)?")  # Not command
async def template_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)

    if message.text.isdigit():
        # Delete template
        number = int(message.text)
        templates = await bot.answers
        if not templates:
            await message.answer(_("你没有模板来删除它们"))
        if number < 0 or number >= len(templates):
            await message.answer(_("编号错误。要删除一个模板，请在0和{0}之间输入一个数字").format(
                len(templates)))
            return
        await templates[number].delete()
    else:
        # Add template
        total_templates = len(await bot.answers)
        if total_templates > 30:
            await message.answer(_("您的机器人已经有太多模板了"))
        else:
            answers = await bot.answers.filter(text=message.text)
            if answers:
                await message.answer(_("此文本已在模板列表中"))
            else:
                template = DefaultAnswer(text=message.text, bot=bot)
                await template.save()

    await send_bot_templates_menu(bot, chat_id=message.chat.id)


@dp.callback_query_handler(menu_callback.filter(), state="*")
async def callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    level = callback_data.get("level")

    if level == "0":
        return await send_bots_menu(call.message.chat.id, call.from_user.id, call)

    bot_id = callback_data.get("bot_id")
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer(_("你对这个机器人没有任何权利"), show_alert=True)
        return

    if level == "1":
        await state.reset_state()
        return await send_bot_menu(bot, call)

    operation = callback_data.get("operation")
    if level == "2":
        await state.reset_state()
        if operation == "chat":
            return await send_chats_menu(bot, call)
        if operation == "delete":
            return await send_bot_delete_menu(bot, call)
        if operation == "stat":
            return await send_bot_statistic_menu(bot, call)
        if operation == "settings":
            return await send_bot_settings_menu(bot, call)
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
        if operation == "threads":
            await bot_actions.threads(bot, call)
            return await send_bot_settings_menu(bot, call)
        if operation == "antiflood":
            await bot_actions.antiflood(bot, call)
            return await send_bot_settings_menu(bot, call)
        if operation == "additional_info":
            await bot_actions.additional_info(bot, call)
            return await send_bot_settings_menu(bot, call)
        if operation == "olgram_text":
            await bot_actions.olgram_text(bot, call)
            return await send_bot_settings_menu(bot, call)
        if operation == "reset_text":
            await bot_actions.reset_bot_text(bot, call)
            return await send_bot_text_menu(bot, call)
        if operation == "next_text":
            await state.set_state("wait_second_text")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_second_text_menu(bot, call)
        if operation == "reset_second_text":
            await bot_actions.reset_bot_second_text(bot, call)
            return await send_bot_second_text_menu(bot, call)
        if operation == "templates":
            await state.set_state("wait_template")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_templates_menu(bot, call)
