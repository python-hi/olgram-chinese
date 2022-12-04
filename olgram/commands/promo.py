"""
这里是促销代码
"""


from aiogram import types
from aiogram.dispatcher import FSMContext
from olgram.models import models
from uuid import UUID

from olgram.router import dp
from olgram.settings import OlgramSettings
from locales.locale import _


@dp.message_handler(commands=["newpromo"], state="*")
async def new_promo(message: types.Message, state: FSMContext):
    """
    命令 /newpromo
    """

    if message.chat.id != OlgramSettings.supervisor_id():
        await message.answer(_("Недостаточно прав"))
        return

    promo = await models.Promo()
    await message.answer(_("Новый промокод\n```{0}```").format(promo.code), parse_mode="Markdown")

    await promo.save()


@dp.message_handler(commands=["delpromo"], state="*")
async def del_promo(message: types.Message, state: FSMContext):
    """
    命令 /delpromo
    """

    if message.chat.id != OlgramSettings.supervisor_id():
        await message.answer(_("权限不够"))
        return

    try:
        uuid = UUID(message.get_args().strip())
        promo = await models.Promo.get_or_none(code=uuid)
    except ValueError:
        return await message.answer(_("错误的令牌"))

    if not promo:
        return await message.answer(_("不存在这样的代码"))

    user = await models.User.filter(promo=promo)
    bots = await user.bots()
    for bot in bots:
        bot.enable_olgram_text = True
        await bot.save(update_fields=["enable_olgram_text"])

    await promo.delete()

    await message.answer(_("促销代码已撤销"))


@dp.message_handler(commands=["setpromo"], state="*")
async def setpromo(message: types.Message, state: FSMContext):
    """
    命令 /setpromo
    """

    arg = message.get_args()
    if not arg:
        return await message.answer(_("指定参数：促销代码。 例如: <pre>/setpromo my-promo-code</pre>"),
                                    parse_mode="HTML")

    arg = arg.strip()

    try:
        UUID(arg)
    except ValueError:
        return await message.answer(_("未找到促销代码"))

    promo = await models.Promo.get_or_none(code=arg)
    if not promo:
        return await message.answer(_("未找到促销代码"))

    if promo.owner:
        return await message.answer(_("促销代码已使用"))

    user, created = await models.User.get_or_create(telegram_id=message.from_user.id)
    promo.owner = user
    await promo.save(update_fields=["owner_id"])

    await message.answer(_("促销代码激活！ 谢谢 🙌"))
