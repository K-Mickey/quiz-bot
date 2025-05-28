import asyncio
import logging

from bin.tg import run_bot, settings

if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    asyncio.run(run_bot(bot_token=settings.TOKEN, redis_url=settings.REDIS_URL))
