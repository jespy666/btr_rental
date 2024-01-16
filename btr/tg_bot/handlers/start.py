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
    _kb = InlineMenuKB().place_to_start()

    @staticmethod
    async def handle(message: Message, bot: Bot):
        user_id = message.from_user.id
        await bot.send_message(user_id, Start._msg, reply_markup=Start._kb)

    @staticmethod
    async def callback_handle(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(Start._msg, reply_markup=Start._kb)
        await call.answer()
        await state.clear()
