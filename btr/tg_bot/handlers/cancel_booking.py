from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from django.core.exceptions import ObjectDoesNotExist

from ..keyboards.kb_cancel import CancelKB
from ..keyboards.kb_dialog import DialogKB
from ..states.cancel import BookCancelState

from django.utils.translation import gettext as _

from ..utils.exceptions import InvalidEmailError, WrongPasswordError, \
    WrongIDError
from ..utils.validators import validate_email, validate_pks
from ...orm_utils import check_user_exist_as, check_password_as, \
    get_username_as, get_user_bookings_as, cancel_booking_as


class CancelRide:

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<strong>Cancel booking</strong>\n\n'
            '<em>To cancel booking, type account email</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(BookCancelState.email)

    @staticmethod
    async def ask_password(message: Message, state: FSMContext, bot: Bot):
        email = message.text.lower()
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_email(email)
            await check_user_exist_as(email)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>User with email <strong>{email}</strong> find '
                'successfully!</em>\n\n'
            ).format(email=email)
            msg2 = _(
                '<em>To confirm your identity,'
                ' please enter your account password</em>'
            )
            await bot.send_message(user_id, msg)
            await bot.send_message(user_id, msg2, reply_markup=kb)
            await state.update_data(email=email)
            await state.set_state(BookCancelState.password)
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
    async def choose_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        password = message.text
        user_id = message.from_user.id
        email = data.get('email')
        kb = CancelKB().place()
        try:
            await check_password_as(email, password)
            username = await get_username_as(email)
            bookings = await get_user_bookings_as(email)
            bookings_id = bookings.get('bookings_id')
            bookings_data = bookings.get('bookings_data')
            if not bookings_id:
                msg = _(
                    '➖➖➖\n\n'
                    '<em><strong>Hi, {username}!</strong>\n\n'
                    'There are no bookings on your account!\n\n'
                    'To sign up for a rental, select the /book command!</em>'
                ).format(username=username)
                await bot.send_message(user_id, msg)
                await state.clear()
            else:
                kb_reply = DialogKB(bookings_id).place()
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<strong>Hi, {username}!</strong>\n\n'
                    '<em>Your bookings ↙️\n\n</em>'
                    '{bookings}'
                ).format(
                    username=username,
                    bookings='\n'.join(bookings_data),
                )
                msg2 = _(
                    '<em>Select the booking ID you want to cancel ⤵️</em>'
                )
                await bot.send_message(user_id, msg, reply_markup=kb)
                await bot.send_message(user_id, msg2, reply_markup=kb_reply)
                await state.update_data(pks=bookings_id, ids_kb=kb_reply)
                await state.set_state(BookCancelState.pk)
        except WrongPasswordError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Wrong password!</strong>\n\n'
                '<em>If you have lost access to your account,\n'
                'select <strong>/reset</strong>'
                ' command\nOr type password again ↙️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def confirm_cancel(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        pk = message.text
        bookings_id = data.get('pks')
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_pks(pk, bookings_id)
            confirm = [_('Confirm'),]
            kb_reply = DialogKB(confirm).place()
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Are you sure, to cancel ride #{pk}?</em>'
            ).format(pk=pk)
            msg2 = _(
                '<em>If so, type <strong>Confirm</strong> button below ⤵️\n'
                'Otherwise, just cancel the dialog</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(pk=pk, confirm_kb=kb_reply)
            await state.set_state(BookCancelState.confirm)
        except WrongIDError:
            kb_reply = data.get('ids_kb')
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Incorrect ID!</strong>\n'
            )
            msg2 = _(
                '<em>Please select ID from the options below ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)

    @staticmethod
    async def cancel_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        user_id = message.from_user.id
        pk = data.get('pk')
        email = data.get('email')
        await cancel_booking_as(pk, email)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Booking #{pk} are canceled!</strong>\n\n'
            'If you cancel your booking by mistake,\n'
            'You can re-book for the same time\n\n'
            'Or choose a different one using the '
            '<strong>/book</strong> command!</em>'
        ).format(pk=pk)
        await bot.send_message(user_id, msg)
        await state.clear()
