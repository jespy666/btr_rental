from aiogram.fsm.state import StatesGroup, State


class BookCancelState(StatesGroup):
    email = State()
    password = State()
    pk = State()
    confirm = State()
