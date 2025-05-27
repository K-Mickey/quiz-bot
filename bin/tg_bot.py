from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from bin.tg_handlers import router


async def run_bot(bot_token: str, redis_url: str):
    async with Bot(token=bot_token).context() as bot:
        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Запустить бота"),
            ]
        )

        storage = RedisStorage.from_url(redis_url)
        dp = Dispatcher(storage=storage)
        dp.include_router(router)
        await dp.start_polling(bot)
