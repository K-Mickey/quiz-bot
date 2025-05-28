import logging

from bin.vk import settings, run_bot

if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    run_bot(bot_token=settings.TOKEN)
