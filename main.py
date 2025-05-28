import logging

from bin import settings
from bin.vk.bot import run_bot

if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    # asyncio.run(run_bot(bot_token=settings.TG_TOKEN, redis_url=settings.REDIS_URL))

    run_bot(bot_token=settings.VK_TOKEN, redis_url=settings.VK_REDIS_URL)
