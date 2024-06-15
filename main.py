import asyncio
import logging
import sys

from bot import BotConfig
from database import Database


async def start_bot():
    database = Database()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot_config = BotConfig(database)
    await bot_config.start()


async def main():
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
