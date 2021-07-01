from tortoise import Tortoise
from olgram.settings import DatabaseSettings


async def init_database():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url=f'postgres://{DatabaseSettings.user()}:{DatabaseSettings.password()}'
               f'@localhost:5430/{DatabaseSettings.database_name()}',
        modules={'models': ['olgram.models.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()
