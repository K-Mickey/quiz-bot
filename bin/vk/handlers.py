import logging
import re
from dataclasses import asdict

from vkbottle import Keyboard
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from .filters import StateRule
from .states import States
from ..redis import RedisStateManager
from ..read_questions import Question, get_random_question

log = logging.getLogger(__name__)
labeler = BotLabeler()


@labeler.message(text="Начать")
async def start(message: Message):
    keyboard = Keyboard().schema(
        [
            [
                {"label": "Новый вопрос", "type": "text"},
                {"label": "Сдаться", "type": "text"},
            ],
            [{"label": "Мой счёт", "type": "text"}],
        ]
    )
    log.debug(f"User {message.from_id} started the bot")
    await message.answer("Привет! Я бот для викторин!", keyboard=keyboard)


@labeler.message(text="Новый вопрос")
async def new_question(message: Message, state_manager: RedisStateManager):
    question: Question = get_random_question()
    state_manager.set_state(message.from_id, States.AWAIT_ANSWER)
    state_manager.set_data(message.from_id, asdict(question))

    log.debug(f"For user {message.from_id} new question: {question}")
    await message.answer(f"Вопрос: {question.question}")


@labeler.message(StateRule(States.AWAIT_ANSWER), text="Сдаться")
async def give_up(message: Message, state_manager: RedisStateManager):
    state_manager.delete_state(message.from_id)

    bot_data = state_manager.get_data(message.from_id)
    question = Question(**bot_data or {})
    state_manager.delete_data(message.from_id)

    log.debug(f"For user {message.from_id} give up: {question}")
    await message.answer(f"Правильный ответ: {question.answer}")

    await new_question(message, state_manager)



@labeler.message(StateRule(States.AWAIT_ANSWER))
async def quiz_answer(message: Message, state_manager: RedisStateManager):
    bot_data = state_manager.get_data(message.from_id)
    question = Question(**bot_data or {})

    real_answer = question.answer.lower()
    root_answer = re.search(r"[\w\s,]+", real_answer).group()
    user_answer = message.text.lower()

    if root_answer == user_answer:
        message_text = (
            "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
        state_manager.delete_state(message.from_id)
        state_manager.delete_data(message.from_id)
    else:
        message_text = "Неправильно… Попробуешь ещё раз?"

    log.debug(
        f"For user {message.from_id} answer: {message.text}, right answer: {question.answer}"
    )
    await message.answer(message_text)
