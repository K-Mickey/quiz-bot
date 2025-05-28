import logging
import re
from dataclasses import asdict

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from ..read_questions import Question, get_random_question
from .states import Quiz

log = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
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


@router.message(F.text == "Новый вопрос")
async def new_question(message: Message, state: FSMContext):
    question: Question = get_random_question()
    await state.update_data(question=asdict(question))  # noqa
    await state.set_state(Quiz.await_answer)

    log.debug(f"For user {message.from_user.id} new question: {question}")
    await message.answer(f"Вопрос: {question.question}")


@router.message(F.text == "Сдаться", Quiz.await_answer)
async def give_up(message: Message, state: FSMContext):
    data = await state.get_data()
    question = Question(**data["question"])
    await state.clear()

    log.debug(f"For user {message.from_user.id} give up: {question}")
    await message.answer(f"Правильный ответ: {question.answer}")

    await new_question(message, state)


@router.message(F.text, Quiz.await_answer)
async def quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = Question(**data["question"])

    real_answer = question.answer.lower()
    root_answer = re.search(r"[\w\s,]+", real_answer).group()
    user_answer = message.text.lower()

    if root_answer == user_answer:
        message_text = (
            "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
        await state.clear()
    else:
        message_text = "Неправильно… Попробуешь ещё раз?"

    log.debug(
        f"For user {message.from_user.id} answer: {message.text}, right answer: {question.answer}"
    )
    await message.answer(message_text)
