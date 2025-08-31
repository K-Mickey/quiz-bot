import asyncio
import logging

from vkbottle import ABCRule, Bot, Keyboard
from vkbottle.bot import Message

import settings
from state_manager import RedisStateManager
from utils import States, check_user_answer, end_quiz, start_quiz

log = logging.getLogger(__name__)


class StateRule(ABCRule[Message]):
    def __init__(self, state: str):
        self.state = state

    async def check(self, event: Message):
        user_state = await state_manager.state.get(event.from_id)
        return user_state == self.state


async def start(message: Message):
    log.debug(f"User {message.from_id} started the bot")
    keyboard = Keyboard().schema(
        [
            [
                {"label": "Новый вопрос", "type": "text"},
                {"label": "Сдаться", "type": "text"},
            ],
            [{"label": "Мой счёт", "type": "text"}],
        ]
    )
    await message.answer("Привет! Я бот для викторин!", keyboard=keyboard)


async def new_question(message: Message):
    log.debug(f"Start quiz for user {message.from_id}")
    quiz = await start_quiz(state_manager=state_manager, user_id=message.from_id)
    await message.answer(f"Вопрос: {quiz.question}")


async def give_up(message: Message):
    log.debug(f"User {message.from_id} give up")
    quiz = await end_quiz(state_manager=state_manager, user_id=message.from_id)
    await message.answer(f"Правильный ответ: {quiz.answer}")
    await new_question(message)


async def quiz_answer(message: Message):
    log.debug(f"User {message.from_id} send answer")
    user_id = message.from_id

    message_text = "Неправильно… Попробуешь ещё раз?"
    if await check_user_answer(state_manager=state_manager, user_id=user_id, answer=message.text):
        message_text = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        await end_quiz(state_manager=state_manager, user_id=user_id)

    await message.answer(message_text)


def run_bot(bot_token: str):
    bot = Bot(bot_token)
    bot.on.message(text="Начать")(start)
    bot.on.message(text="Новый вопрос")(new_question)
    bot.on.message(StateRule(States.AWAIT_ANSWER), text="Сдаться")(give_up)
    bot.on.message(StateRule(States.AWAIT_ANSWER))(quiz_answer)
    bot.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    state_manager = RedisStateManager(redis_url=settings.REDIS_URL, prefix="vk")

    try:
        run_bot(bot_token=settings.VK_TOKEN)
    finally:
        asyncio.run(state_manager.disconnect())
