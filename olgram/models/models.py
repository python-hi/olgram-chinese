from tortoise.models import Model
from tortoise import fields


class Bot(Model):
    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=50, unique=True)
    owner = fields.ForeignKeyField("models.User", related_name="bots")
    name = fields.CharField(max_length=33)

    class Meta:
        table = 'bot'


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(index=True, unique=True)

    class Meta:
        table = 'user'
