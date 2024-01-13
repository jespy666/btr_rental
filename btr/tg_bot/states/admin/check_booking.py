from aiogram.fsm.state import StatesGroup, State


class CheckBookingState(StatesGroup):
    bookingId = State()
