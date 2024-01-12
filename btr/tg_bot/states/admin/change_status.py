from aiogram.fsm.state import StatesGroup, State


class ChangeStatusState(StatesGroup):
    bookingId = State()
    bookingStatus = State()
