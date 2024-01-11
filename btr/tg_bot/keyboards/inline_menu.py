from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _


class InlineMenuKB:

    def __init__(self):
        self.kb = InlineKeyboardBuilder()

    def place(self):
        items = {
            _('Book a ride'): 'book',
            _('See help'): 'help',
            _('Create account'): 'create',
            _('Reset password'): 'reset',
            _('Main menu'): 'start',
        }
        for item, callback in items.items():
            self.kb.button(
                text=item,
                callback_data=callback,
            )
        self.kb.adjust(2)
        return self.kb.as_markup()
