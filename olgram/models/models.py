from tortoise.models import Model
from tortoise import fields
from uuid import uuid4
from textwrap import dedent


class Bot(Model):
    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=50, unique=True)
    owner = fields.ForeignKeyField("models.User", related_name="bots")
    name = fields.CharField(max_length=33)
    code = fields.UUIDField(default=uuid4, index=True)
    start_text = fields.TextField(default=dedent("""
    Здравствуйте!
    Напишите ваш вопрос и мы ответим вам в ближайшее время.
    """))

    group_chats = fields.ManyToManyField("models.GroupChat", related_name="bots", on_delete=fields.relational.CASCADE,
                                         null=True)
    group_chat = fields.ForeignKeyField("models.GroupChat", related_name="active_bots",
                                        on_delete=fields.relational.CASCADE,
                                        null=True)

    async def super_chat_id(self):
        group_chat = await self.group_chat
        if group_chat:
            return group_chat.chat_id
        return (await self.owner).telegram_id

    class Meta:
        table = 'bot'


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(index=True, unique=True)

    class Meta:
        table = 'user'


class GroupChat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.IntField(index=True, unique=True)
    name = fields.CharField(max_length=50)

    class Meta:
        table = 'group_chat'
