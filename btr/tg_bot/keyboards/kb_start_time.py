from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class StartTimesKB:

    def __init__(self, buttons):
        self.buttons = buttons

    def place_outline(self):
        buttons = [[KeyboardButton(text=button) for button in self.buttons]]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
