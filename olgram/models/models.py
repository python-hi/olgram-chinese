from tortoise.models import Model
from tortoise import fields

from textwrap import dedent


class Bot(Model):
    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=50, unique=True)
    owner = fields.ForeignKeyField("models.User", related_name="bots")
    name = fields.CharField(max_length=33)
    start_text = fields.TextField(default=dedent("""
    Здравствуйте!
    Напишите ваш вопрос и мы ответим Вам в ближайшее время.
    """))

    super_chat_id = fields.IntField()
    group_chats = fields.ManyToManyField("models.GroupChat", related_name="bots", on_delete=fields.relational.SET_NULL)

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
