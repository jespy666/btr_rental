from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.utils.translation import gettext as _

from ..keyboards.kb_cancel import CancelKB
from ..keyboards.kb_dialog import DialogKB
from ..states.cancel_booking import BookCancelState
from ..utils.decorators import validators
from ..utils.handlers import vk_notify, mail_notify
from ..utils.validators import validate_email, validate_pks
from ...orm_utils import AsyncTools


class CancelRide:
    status = _('canceled')

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<em><strong>Cancel booking</strong>\n\n'
            'To cancel booking, type account email</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(BookCancelState.email)

    @staticmethod
    @validators
    async def ask_password(message: Message, state: FSMContext, bot: Bot):
        email = message.text.lower()
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_email(email)
        user_info = await AsyncTools().get_user_info(email=email)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>User with email <strong>{email}</strong>\n'
            'Find successfully!</em>\n\n'
        ).format(email=email)
        msg2 = _(
            '<em>To confirm your identity,\n'
            'please enter your account password</em>'
        )
        await bot.send_message(user_id, msg)
        await bot.send_message(user_id, msg2, reply_markup=kb)
        await state.update_data(user_info=user_info)
        await state.set_state(BookCancelState.password)

    @staticmethod
    @validators
    async def choose_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        password = message.text
        user_id = message.from_user.id
        user_info = data.get('user_info')
        email = user_info.get('email')
        username = user_info.get('username')
        kb = CancelKB().place()
        await AsyncTools().check_password(password, email=email)
        bookings = await AsyncTools().get_user_bookings(email=email)
        bookings_id = bookings.get('bookings_id')
        bookings_data = bookings.get('bookings_data')
        if not bookings_id:
            msg = _(
                '➖➖➖\n\n'
                '<em><strong>Hi, {username}!</strong>\n\n'
                'There are no bookings on your account!\n\n'
                'To sign up for a rental,\nselect the /book command!</em>'
            ).format(username=username)
            await bot.send_message(user_id, msg)
            await state.clear()
        else:
            kb_reply = DialogKB(bookings_id).place()
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Hi, <strong>{username}</strong>!\n\n'
                'Your bookings ↙️\n\n'
                '<strong>{bookings}</strong></em>'
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

    @staticmethod
    @validators
    async def confirm_cancel(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        pk = message.text
        bookings_id = data.get('pks')
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_pks(pk, bookings_id)
        booking_info = await AsyncTools().get_booking_info(pk=pk)
        confirm = [_('Confirm'),]
        kb_reply = DialogKB(confirm).place()
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Are you sure, to cancel ride #{pk}?</strong></em>'
        ).format(pk=pk)
        msg2 = _(
            '<em>If so, type <strong>Confirm</strong> button below ⤵️\n'
            'Otherwise, just cancel the dialog</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(pk=pk, confirm_kb=kb_reply,
                                booking_info=booking_info)
        await state.set_state(BookCancelState.confirm)

    @staticmethod
    async def cancel_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        user_info = data.get('user_info')
        booking_info = data.get('booking_info')
        friendly_date = booking_info.get('friendly_date')
        user_id = message.from_user.id
        pk = data.get('pk')
        booking_info.update(user_info)
        await AsyncTools().modify_booking(pk, status=CancelRide.status)
        booking_info['status'] = CancelRide.status
        booking_info['pk'] = pk
        booking_info['date'] = friendly_date
        vk_notify(False, False, **booking_info)
        mail_notify('self_cancel', **booking_info)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Booking #{pk} are canceled!</strong>\n\n'
            'If you cancel your booking by mistake,\n'
            'You can re-book for the same time\n\n'
            'Or choose a different one using the\n'
            '<strong>/book</strong> command!</em>'
        ).format(pk=pk)
        await bot.send_message(user_id, msg)
        await state.clear()
