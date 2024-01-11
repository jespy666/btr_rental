from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from django.utils.translation import gettext as _

from ..keyboards.inline_menu import InlineMenuKB


class Start:
    _msg = _(
        '<strong>16+❗️</strong>\n\n'
        '<em>Hi!\nI\'m BroTeamRacing Bot!\n'
        'With my help, you\'ll be able to:</em>\n\n'
        '👤 <strong>Quick Sign Up</strong>\n\n'
        '📆 <strong>Make Bookings</strong>\n\n'
        '🔓 <strong>Reset your password</strong>\n\n'
        '📱 <strong>Get our contacts</strong>\n'
    )

    @staticmethod
    async def handle(message: Message, bot: Bot):
        await bot.send_message(
            message.from_user.id,
            Start._msg,
        )

    @staticmethod
    async def callback_handle(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(
            Start._msg,
            reply_markup=InlineMenuKB().place()
        )
        await call.answer()
        await state.clear()
