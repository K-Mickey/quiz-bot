from vkbottle import Bot

from .handlers import labeler
from .middlewares import StateMiddleware


def run_bot(bot_token: str):
    bot = Bot(
        token=bot_token,
        labeler=labeler,
    )

    bot.labeler.message_view.register_middleware(StateMiddleware)
    bot.run_forever()
