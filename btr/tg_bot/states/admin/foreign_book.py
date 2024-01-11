from aiogram.fsm.state import StatesGroup, State


class ForeignBookingState(StatesGroup):
    outBikes = State()
    outPhone = State()
    outDate = State()
    outStart = State()
    outHours = State()
