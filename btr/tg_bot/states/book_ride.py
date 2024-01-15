from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    bookEmail = State()
    bookBikes = State()
    bookDate = State()
    bookStart = State()
    bookHours = State()
