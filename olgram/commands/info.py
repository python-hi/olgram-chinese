"""
这里的指标
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from olgram.models import models

from olgram.router import dp
from olgram.settings import OlgramSettings
from locales.locale import _


@dp.message_handler(commands=["info"], state="*")
async def info(message: types.Message, state: FSMContext):
    """
    命令 /info
    """

    if message.chat.id != OlgramSettings.supervisor_id():
        await message.answer(_("权限不够"))
        return

    bots = await models.Bot.all()
    bots_count = len(bots)
    user_count = len(await models.User.all())
    templates_count = len(await models.DefaultAnswer.all())
    promo_count = len(await models.Promo.all())
    olgram_text_disabled = len(await models.Bot.filter(enable_olgram_text=False))

    income_messages = sum([bot.incoming_messages_count for bot in bots])
    outgoing_messages = sum([bot.outgoing_messages_count for bot in bots])

    await message.answer(_("机器人数量: {0}\n").format(bots_count) +
                         _("用户数（用于构造函数）: {0}\n").format(user_count) +
                         _("答案模板: {0}\n").format(templates_count) +
                         _("所有机器人的传入消息: {0}\n").format(income_messages) +
                         _("所有机器人的传出消息: {0}\n").format(outgoing_messages) +
                         _("已发布促销代码: {0}\n").format(promo_count) +
                         _("广告牌关了: {0}\n".format(olgram_text_disabled)))
