from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from btr.tasks.reg_tasks import (send_verification_code_from_tg,
                                 send_recover_message_from_tg)

from ..keyboards.kb_cancel import CancelKB
from ..states.reset_password import ResetPasswordState
from ..utils.validators import validate_email
from ..utils.handlers import generate_verification_code, \
    check_verification_code
from ..utils.exceptions import InvalidEmailError, CompareCodesError
from ...orm_utils import check_user_exist_as, reset_user_password_as


class ResetPassword:

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<strong>Password reset</strong>\n\n'
            '<em>To reset your forgotten password, please type your '
            'valid email</em>\n\n'
            '⚠️ <strong>Case sensitive</strong> ⤵️'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(ResetPasswordState.resetEmail)

    @staticmethod
    async def ask_code(message: Message, state: FSMContext, bot: Bot):
        email = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_email(email)
            await check_user_exist_as(email)
            verification_code = generate_verification_code()
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>User with email <strong>{email}</strong> find '
                'successfully!\n\n'
                'Verification code was sent to your mail!\n\n'
                'Type the six-digit code from the email</em> ⤵️'
            ).format(email=email)
            send_verification_code_from_tg.delay(email, verification_code)
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.update_data(code=verification_code, email=email)
            await state.set_state(ResetPasswordState.verificationCode)
        except InvalidEmailError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid email format <em>{email}</em></strong>\n\n'
                '<em>Check your spelling and try again</em> ⤵️'
            ).format(email=email)
            await bot.send_message(user_id, msg, reply_markup=kb)
        except ObjectDoesNotExist:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>User with email {email} does not exist!</strong>\n\n'
                '<em>Do not have an account?\n'
                '- Cancel dialog and choose /create command!\n\n'
                'Or try again</em> ⤵️'
            ).format(email=email)
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def reset_password(message: Message, state: FSMContext, bot: Bot):
        reset_data = await state.get_data()
        user_code = message.text
        code = reset_data.get('code')
        email = reset_data.get('email')
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            check_verification_code(code, user_code)
            password = await reset_user_password_as(email)
            send_recover_message_from_tg.delay(email, password)
            msg = _(
                '🎉🎉🎉\n\n'
                '<em>Your password has been reset successfully!\n\n'
                'New password and other details was send to</em> ↙️\n\n'
                '✉️ <strong>{email}</strong>'
            ).format(email=email)
            await bot.send_message(user_id, msg)
            await state.clear()
        except CompareCodesError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Wrong verification code!\n\n'
                '⚠️ Case sensitive!</strong>\n\n'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
