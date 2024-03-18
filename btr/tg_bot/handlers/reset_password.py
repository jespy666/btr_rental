from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.utils.translation import gettext as _

from btr.tasks.users import send_verification_code, send_recover_message

from ..keyboards.kb_cancel import CancelKB
from ..states.reset_password import ResetPasswordState
from ..utils.decorators import validators
from ..utils.validators import validate_email
from ..utils.handlers import (generate_verification_code,
                              check_verification_code)
from ...orm_utils import AsyncTools


class ResetPassword:

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<em><strong>Password reset</strong>\n\n'
            'To reset your forgotten password,\n'
            'type <strong>email</strong> from your account</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(ResetPasswordState.resetEmail)

    @staticmethod
    @validators
    async def ask_code(message: Message, state: FSMContext, bot: Bot):
        email = message.text.lower()
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_email(email)
        user_info = await AsyncTools().get_user_info(email=email)
        verification_code = generate_verification_code()
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>User find successfully!\n\n'
            'Verification code was sent to ↙️\n\n'
            '✉️ <strong>{email}</strong>\n\n'
            'Type the six-digit code from the email</em> ⤵️'
        ).format(email=email)
        send_verification_code.delay(email=email, code=verification_code)
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(code=verification_code, user_info=user_info)
        await state.set_state(ResetPasswordState.verificationCode)

    @staticmethod
    @validators
    async def reset_password(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        user_code = message.text
        user_info = data.get('user_info')
        code = data.get('code')
        email = user_info.get('email')
        user_id = message.from_user.id
        check_verification_code(code, user_code)
        password = await AsyncTools().reset_password(email=email)
        send_recover_message.delay(password=password, **user_info)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em>Your password has been reset successfully!\n\n'
            'New password was send to ↙️\n\n'
            '✉️ <strong>{email}</strong></em>'
        ).format(email=email)
        await bot.send_message(user_id, msg)
        await state.clear()
