from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _


class InlineMenuKB:

    def __init__(self):
        self.kb = InlineKeyboardBuilder()
        self.items = {
            _('Book a ride'): 'book',
            _('See help'): 'help',
            _('Create account'): 'create',
            _('Reset password'): 'reset',
            _('Cancel booking'): 'cancel',
        }

    def place(self):
        self.items[_('Main menu')] = 'start'
        for item, callback in self.items.items():
            self.kb.button(
                text=item,
                callback_data=callback,
            )
        self.kb.adjust(2)
        return self.kb.as_markup()

    def place_to_start(self):
        self.items[_('See prices')] = 'price'
        for item, callback in self.items.items():
            self.kb.button(
                text=item,
                callback_data=callback,
            )
        self.kb.adjust(2)
        return self.kb.as_markup()
