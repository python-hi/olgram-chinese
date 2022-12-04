import aiogram.types as types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
import typing as ty
from locales.locale import _


def public():
    """
    即使用户不是机器人的所有者，也会处理带有此装饰器的处理程序
     （例如，/help 命令）
    :return:
    """

    def decorator(func):
        setattr(func, "access_public", True)
        return func

    return decorator


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_chat_ids: ty.Iterable[int]):
        self._access_chat_ids = access_chat_ids
        super(AccessMiddleware, self).__init__()

    @classmethod
    def _is_public_command(cls) -> bool:
        handler = current_handler.get()
        return handler and getattr(handler, "access_public", False)

    async def on_process_message(self, message: types.Message, data: dict):
        admin_ids = self._access_chat_ids
        if not admin_ids:
            return  # 完全未指定机器人管理员

        if self._is_public_command():  # 允许所有用户使用此命令
            return

        if message.chat.id not in admin_ids:
            await message.answer(_("机器人所有者已限制访问此功能 😞"))
            raise CancelHandler()

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        admin_ids = self._access_chat_ids
        if not admin_ids:
            return  # 完全未指定机器人管理员

        if self._is_public_command():  # 允许所有用户使用此命令
            return

        if call.message.chat.id not in admin_ids:
            await call.answer(_("机器人所有者已限制访问此功能😞"))
            raise CancelHandler()
