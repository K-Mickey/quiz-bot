from vkbottle import BaseMiddleware
from vkbottle.bot import Message

from . import settings
from ..redis import RedisStateManager


class StateMiddleware(BaseMiddleware[Message]):
    async def pre(self) -> None:
        state_manager = RedisStateManager(settings.REDIS_URL)
        self.send({"state_manager": state_manager})
