from vkbottle import Bot

from .handlers import labeler
from .middlewares import StateMiddleware
from ..db import RedisStateManager


def run_bot(bot_token: str, redis_url: str):
    bot = Bot(
        token=bot_token,
        labeler=labeler,
    )

    redis = RedisStateManager(redis_url)
    StateMiddleware.configure(redis)
    bot.labeler.message_view.register_middleware(StateMiddleware)

    bot.run_forever()
