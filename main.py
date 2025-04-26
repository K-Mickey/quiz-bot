import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message

from bin import settings

logger = logging.getLogger(__name__)


async def run_bot(bot_token: str):
    async with Bot(token=bot_token).context() as bot:
        await bot.set_my_commands(
            commands=[
                BotCommand(command='start', description='Запустить бота'),
            ]
        )

        dp = Dispatcher()
        dp.message.register(echo)
        await dp.start_polling(bot)


async def echo(message: Message):
    await message.answer(message.text)


if __name__ == '__main__':
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    asyncio.run(run_bot(bot_token=settings.TG_TOKEN))
