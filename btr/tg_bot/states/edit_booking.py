from aiogram.fsm.state import StatesGroup, State


class EditBookingState(StatesGroup):
    email = State()
    password = State()
    pk = State()
    start = State()
    end = State()
    bikes = State()
