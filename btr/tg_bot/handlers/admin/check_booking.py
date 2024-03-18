from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.utils.translation import gettext as _

from btr.orm_utils import AsyncTools

from ...keyboards.kb_cancel import CancelKB
from ...states.admin.check_booking import CheckBookingState
from ...utils.decorators import validators
from ...utils.validators import validate_id
from ...utils.handlers import check_admin_access, get_emoji_for_status


class CheckBooking:

    @staticmethod
    async def ask_id(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n\n'
                'To see full booking info type an '
                '<strong>ID</strong></em> ⤵️\n\n'
            ).format(admin=user_name if user_name else 'Admin')
            kb = CancelKB().place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.set_state(CheckBookingState.bookingId)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>ACCESS DENIED!</strong>\n\n'
                'You are not the Admin!\n\n'
                '😜 Get lost</em>'
            )
            await bot.send_message(user_id, msg)
            await state.clear()

    @staticmethod
    @validators
    async def show_booking_info(message: Message, state: FSMContext, bot: Bot):
        pk = message.text
        user_id = message.from_user.id
        validate_id(pk)
        booking_info = await AsyncTools().get_booking_info(
            load_prefetch='rider', pk=pk
        )
        user_info = await AsyncTools().get_user_info(
            pk=booking_info.get('rider_id')
        )
        status = booking_info.get('status')
        is_admin = booking_info.get('f_phone')
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Booking #{id} find successfully!</strong>\n\n'
            '👤 Rider: <strong>{rider}</strong>\n\n'
            '📞 Contact: <strong>{phone}</strong>\n\n'
            '🏍 Bikes rented: <strong>{bikes}</strong>\n\n'
            '📆 Booking date: <strong>{date}</strong>\n\n'
            '🕛 Start time: <strong>{start}</strong>\n\n'
            '🕜 End time: <strong>{end}</strong>\n\n'
            'Status ↙️\n\n{emoji} <strong>{status}</strong></em>'
        ).format(
            id=pk,
            rider=user_info.get('username'),
            phone=is_admin if is_admin else user_info.get('phone'),
            bikes=booking_info.get('bikes'),
            date=booking_info.get('friendly_date'),
            start=booking_info.get('start'),
            end=booking_info.get('end'),
            emoji=get_emoji_for_status(status),
            status=status,
        )
        await bot.send_message(user_id, msg)
        await state.clear()
