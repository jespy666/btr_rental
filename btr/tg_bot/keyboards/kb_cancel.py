from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from django.utils.translation import gettext as _


class CancelKB:

    def __init__(self):
        self.kb = InlineKeyboardBuilder()
        self.cancel_button = InlineKeyboardButton(
            text=_('Cancel dialog'),
            callback_data='cancel-dialog',
        )

    def place(self):
        self.kb.add(self.cancel_button)
        self.kb.adjust(1)
        return self.kb.as_markup()
