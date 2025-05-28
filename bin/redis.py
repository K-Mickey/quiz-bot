import json

from redis import Redis


class RedisStateManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, redis_url: str):
        self.__redis = Redis.from_url(redis_url)

    def close(self) -> None:
        self.__redis.close()

    def get_state(self, user_id: int) -> str | None:
        value = self.__redis.get(f"user:{user_id}:state")
        return value.decode("utf-8") if value else None

    def set_state(self, user_id: int, state: str) -> None:
        self.__redis.set(f"user:{user_id}:state", state)

    def delete_state(self, user_id: int) -> None:
        self.__redis.delete(f"user:{user_id}:state")

    def get_data(self, user_id: int) -> dict | None:
        value = self.__redis.get(f"user:{user_id}:data")
        return json.loads(value.decode("utf-8")) if value else None

    def set_data(self, user_id: int, value: dict) -> None:
        self.__redis.set(f"user:{user_id}:data", json.dumps(value))

    def delete_data(self, user_id: int) -> None:
        self.__redis.delete(f"user:{user_id}:data")
