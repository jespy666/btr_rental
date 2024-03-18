from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from django.utils.translation import gettext as _

from ..keyboards.inline_menu import InlineMenuKB


class Help:

    _msg = _(
        '<em><strong>Any issues and questions?</strong>\n'
        'Contact us ↙️↙️↙️\n\n'
        'vk.me/broteamracing\n\n'
        '📞 <strong>+79992350091</strong> Vladimir\n\n'
        '📞 <strong>+79817850451</strong> Alexander\n\n'
        '🌐 <strong>broteamracing.ru/contacts</strong>\n\n'
        '👥 <strong>vk.com/broteamracing</strong></em>\n\n'
    )

    @staticmethod
    async def handle(message: Message, bot: Bot):
        await bot.send_message(
            message.from_user.id,
            Help._msg,
        )

    @staticmethod
    async def callback_handle(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(
            Help._msg,
            reply_markup=InlineMenuKB().place()
        )
        await call.answer()
        await state.clear()
