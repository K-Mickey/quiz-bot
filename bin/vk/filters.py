from vkbottle import ABCRule
from vkbottle.bot import Message

from . import settings
from ..redis import RedisStateManager


class StateRule(ABCRule[Message]):
    def __init__(self, state: str):
        self.state = state

    async def check(self, event: Message):
        state_manager = RedisStateManager(settings.REDIS_URL)
        user_state = state_manager.get_state(event.from_id) or ''
        return user_state == self.state
