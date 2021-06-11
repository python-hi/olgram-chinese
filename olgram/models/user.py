from tortoise import Model, fields


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(index=True)

    class Meta:
        table = 'user'
