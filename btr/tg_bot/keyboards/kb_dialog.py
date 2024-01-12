from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class DialogKB:
    def __init__(self, buttons: list):
        self.buttons = [[KeyboardButton(text=button) for button in buttons]]

    def place(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=self.buttons,
            one_time_keyboard=True,
            resize_keyboard=True,
        )
