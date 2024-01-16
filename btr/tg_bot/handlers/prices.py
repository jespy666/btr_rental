from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from django.utils.translation import gettext as _

from ..keyboards.inline_menu import InlineMenuKB


class Prices:
    _msg = _(
        '💵💵💵 <strong>Prices 💵💵💵\n\n'
        '🏍 X-motos 250</strong>\n\n'
        '<strong>⚙️ 250cc\n'
        '🚀 21 hp\n'
        '💰 2000₽ / hour\n\n'
        '🏍 GR-7 300\n\n'
        '⚙️ 300cc\n'
        '🚀 26 hp\n'
        '💰 2500₽ / hour\n\n'
        '🏍 Progasi Ibiza 300\n\n'
        '⚙️ 300cc\n'
        '🚀 27 hp\n'
        '💰 2500₽ / hour'
        '</strong>'
    )
    _kb = InlineMenuKB().place()

    @staticmethod
    async def handle(message: Message, bot: Bot):
        user_id = message.from_user.id
        await bot.send_message(user_id, Prices._msg, reply_markup=Prices._kb)

    @staticmethod
    async def callback_handle(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(Prices._msg, reply_markup=Prices._kb)
        await call.answer()
        await state.clear()
