import json
import logging
from typing import Sequence

from redis.asyncio import Redis

log = logging.getLogger(__name__)


class UserStateManager:
    def __init__(self, redis: Redis, prefix: str):
        self.__redis = redis
        self.prefix = prefix
        self.coding = "utf-8"

    async def get(self, user_id: int) -> str:
        state_key = self._form_key(user_id)
        value = await self.__redis.get(state_key)
        log.debug(f"{state_key} GET: {value}")
        return value.decode(self.coding) if value else ""

    async def set(self, user_id: int, state: str) -> None:
        state_key = self._form_key(user_id)
        await self.__redis.set(state_key, state)
        log.debug(f"{state_key} SET: {state}")

    async def delete(self, user_id: int) -> None:
        state_key = self._form_key(user_id)
        await self.__redis.delete(state_key)
        log.debug(f"{state_key} DELETE")

    def _form_key(self, user_id: int) -> str:
        return f"{self.prefix}:user:{user_id}:state"


class UserQuizManager:
    def __init__(self, redis: Redis, prefix: str):
        self.__redis = redis
        self.prefix = prefix
        self.coding = "utf-8"

    async def get(self, user_id: int) -> int | None:
        question_key = self._form_key(user_id)
        question_number = await self.__redis.get(question_key)
        log.debug(f"{question_key} GET: {question_number}")
        return int(question_number.decode(self.coding)) if question_number else None

    async def set(self, user_id: int, question_number: int) -> None:
        question_key = self._form_key(user_id)
        await self.__redis.set(question_key, question_number)
        log.debug(f"{question_key} SET: {question_number}")

    async def delete(self, user_id: int) -> None:
        question_key = self._form_key(user_id)
        await self.__redis.delete(question_key)
        log.debug(f"{question_key} DELETE")

    def _form_key(self, user_id: int) -> str:
        return f"{self.prefix}:user:{user_id}:question"


class QuestionsManager:
    def __init__(self, redis: Redis):
        self.__redis = redis
        self.questions_key = "questions"
        self.questions_count_key = "questions_count"
        self.coding = "utf-8"

    async def save(self, questions: Sequence[dict]) -> None:
        async with self.__redis.pipeline() as pipe:
            count = await self.__redis.get(self.questions_count_key) or 0
            count = int(count)

            for index, question in enumerate(questions, count + 1):
                quiz_key = self._form_key(index)
                await pipe.hset(self.questions_key, quiz_key, json.dumps(question))

            await pipe.execute()
            await self.__redis.set(self.questions_count_key, count + len(questions))

        log.debug(f"Saved {len(questions)} questions")

    async def get(self, number: int) -> dict:
        quiz_key = self._form_key(number)
        question = await self.__redis.hget(self.questions_key, quiz_key)
        return json.loads(question.decode(self.coding)) if question else {}

    async def get_random(self) -> tuple[int, dict]:
        random_key = await self.__redis.hrandfield(self.questions_key)
        if not random_key:
            return 0, {}

        key_str = random_key.decode(self.coding)
        question_number = int(key_str.split("_")[1])
        question = await self.__redis.hget(self.questions_key, random_key)

        return question_number, json.loads(question.decode(self.coding)) if question else {}

    async def clear(self) -> None:
        await self.__redis.delete(self.questions_key, self.questions_count_key)

    @staticmethod
    def _form_key(number: int) -> str:
        return f"question_{number}"


class RedisStateManager:
    def __init__(self, redis_url: str, prefix: str):
        self.__redis = Redis.from_url(redis_url)
        self.__prefix = prefix

        self.state = UserStateManager(self.__redis, prefix)
        self.quiz = UserQuizManager(self.__redis, prefix)
        self.questions = QuestionsManager(self.__redis)

        log.debug(f"Redis connected: {redis_url}")

    async def disconnect(self):
        await self.__redis.aclose()
        log.debug("Redis disconnected")
