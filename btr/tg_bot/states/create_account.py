from aiogram.fsm.state import StatesGroup, State


class CreateAccountState(StatesGroup):
    regName = State()
    regUsername = State()
    regEmail = State()
    regPhone = State()
