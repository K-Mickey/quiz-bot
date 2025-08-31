import logging
import re
from dataclasses import dataclass
from enum import StrEnum

from state_manager import RedisStateManager

log = logging.getLogger(__name__)

class States(StrEnum):
    AWAIT_ANSWER = "await_answer"


@dataclass(frozen=True, slots=True)
class Quiz:
    question: str = ""
    answer: str = ""


async def start_quiz(state_manager: RedisStateManager, user_id: int) -> Quiz:
    question_number, question = await state_manager.questions.get_random()
    await state_manager.state.set(user_id=user_id, state=States.AWAIT_ANSWER)
    await state_manager.quiz.set(user_id=user_id, question_number=question_number)
    quiz = Quiz(**question)
    log.debug(f"For user {user_id} choose question: {quiz}")
    return quiz


async def end_quiz(state_manager: RedisStateManager, user_id: int) -> Quiz:
    question_number = await state_manager.quiz.get(user_id)
    question = await state_manager.questions.get(question_number)
    quiz = Quiz(**question)

    await state_manager.quiz.delete(user_id)
    await state_manager.state.delete(user_id)

    log.debug(f"For user {user_id} clear question: {quiz}")
    return quiz


async def check_user_answer(state_manager: RedisStateManager, user_id: int, answer: str) -> bool:
    quiz_number = await state_manager.quiz.get(user_id)
    question = await state_manager.questions.get(quiz_number)
    quiz = Quiz(**question)

    real_answer = parse_answer(quiz.answer)
    user_answer = parse_answer(answer)

    log.debug(f"User {user_id} send answer: {answer}; right answer: {quiz.answer}")
    return real_answer == user_answer


def parse_answer(answer: str) -> str:
    real_answer = answer.lower()
    root_answer = re.search(r"[\w\s,]+", real_answer)
    return root_answer.group() if root_answer else real_answer
