import asyncio
import logging
from olgram.migrations.custom import migrate

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(migrate())
