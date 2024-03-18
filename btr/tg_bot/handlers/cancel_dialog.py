from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from django.utils.translation import gettext as _

from ..keyboards.inline_menu import InlineMenuKB


class Cancel:

    _msg = _(
        '🚫🚫🚫\n\n'
        '<em><strong>Dialog has been canceled</strong>\n\n'
        'You can try again, or choose another command</em> ↙️↙️↘️↘️'
    )

    @staticmethod
    async def handle(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(
            Cancel._msg,
            reply_markup=InlineMenuKB().place()
        )
        await call.answer()
        await state.clear()
