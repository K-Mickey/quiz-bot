from vkbottle import BaseMiddleware
from vkbottle.bot import Message

from bin.db import RedisStateManager


class StateMiddleware(BaseMiddleware[Message]):
    _state_manager: RedisStateManager | None = None

    async def pre(self) -> None:
        if not self._state_manager:
            raise RuntimeError("State manager is not configured")

        self.send({"state_manager": self._state_manager})


    @classmethod
    def configure(cls, state_manager):
        cls._state_manager = state_manager
