from aiogram.fsm.state import StatesGroup, State


class ResetPasswordState(StatesGroup):
    resetEmail = State()
    verificationCode = State()
