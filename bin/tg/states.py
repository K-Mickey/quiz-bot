from aiogram.fsm.state import StatesGroup, State


class Quiz(StatesGroup):
    await_answer = State()
