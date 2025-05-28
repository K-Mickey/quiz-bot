from vkbottle import Bot

from . import settings
from .handlers import labeler
from .middlewares import StateMiddleware

import logging


def run_bot(bot_token: str):
    bot = Bot(
        token=bot_token,
        labeler=labeler,
    )

    bot.labeler.message_view.register_middleware(StateMiddleware)
    bot.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    run_bot(bot_token=settings.TOKEN)
