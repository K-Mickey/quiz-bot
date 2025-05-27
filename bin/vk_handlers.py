import logging

from vkbottle import Keyboard
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from bin.read_questions import Question, get_random_question

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
async def new_question(message):
    question: Question = get_random_question()

    log.debug(f"For user {message.from_id} new question: {question}")
    await message.answer(f"Вопрос: {question.question}")
