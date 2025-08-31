import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Filter
from aiogram.types import BotCommand, KeyboardButton, Message, ReplyKeyboardMarkup

import settings
from state_manager import RedisStateManager
from utils import States, check_user_answer, end_quiz, start_quiz

log = logging.getLogger(__name__)

class StateFilter(Filter):
    def __init__(self, state: States):
        self.state = state

    async def __call__(self, message: Message) -> bool:
        user_state = await state_manager.state.get(message.from_user.id)
        return user_state == self.state


async def start(message: Message):
    keyboard = [
        [KeyboardButton(text="Новый вопрос"), KeyboardButton(text="Сдаться")],
        [KeyboardButton(text="Мой счёт")],
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )

    log.debug(f"User {message.from_user.id} started the bot")
    await message.answer("Привет! Я бот для викторин!", reply_markup=reply_markup)


async def new_question(message: Message):
    log.debug(f"Start quiz for user {message.from_user.id}")
    quiz = await start_quiz(state_manager=state_manager, user_id=message.from_user.id)
    await message.answer(f"Вопрос: {quiz.question}")


async def give_up(message: Message):
    log.debug(f"User {message.from_user.id} give up")
    quiz = await end_quiz(state_manager=state_manager, user_id=message.from_user.id)
    await message.answer(f"Правильный ответ: {quiz.answer}")
    await new_question(message)


async def quiz_answer(message: Message):
    log.debug(f"User {message.from_user.id} send answer")
    user_id = message.from_user.id

    message_text = "Неправильно… Попробуешь ещё раз?"
    if await check_user_answer(state_manager=state_manager, user_id=user_id, answer=message.text):
        message_text = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        await end_quiz(state_manager=state_manager, user_id=user_id)

    await message.answer(message_text)


async def run_bot(bot_token: str):
    async with Bot(token=bot_token).context() as bot:
        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Запустить бота"),
            ]
        )

        dp = Dispatcher()

        dp.message.register(start, CommandStart())
        dp.message.register(new_question, F.text == "Новый вопрос")
        dp.message.register(give_up, F.text == "Сдаться", StateFilter(state=States.AWAIT_ANSWER))
        dp.message.register(quiz_answer, F.text, StateFilter(state=States.AWAIT_ANSWER))

        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    state_manager = RedisStateManager(redis_url=settings.REDIS_URL, prefix="tg")

    try:
        asyncio.run(run_bot(bot_token=settings.TG_TOKEN))
    finally:
        asyncio.run(state_manager.disconnect())
