from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _


class InlineCancelKB:

    def __init__(self):
        self.kb = InlineKeyboardBuilder()

    def place(self):
        self.kb.button(
            text=_('Cancel dialog'),
            callback_data='cancel',
        )
        self.kb.adjust(1)
        return self.kb.as_markup()
