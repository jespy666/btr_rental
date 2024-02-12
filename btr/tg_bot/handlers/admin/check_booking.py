from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from btr.orm_utils import check_booking_info_as

from ...keyboards.kb_cancel import CancelKB
from ...states.admin.check_booking import CheckBookingState
from ...utils.handlers import check_admin_access, get_emoji_for_status


class CheckBooking:

    @staticmethod
    async def ask_id(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n'
                'To see full booking info type an '
                '<strong>ID</strong></em> ⤵️\n\n'
            ).format(admin=user_name if user_name else 'Admin')
            kb = CancelKB().place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.set_state(CheckBookingState.bookingId)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>ACCESS DENIED!\n'
                'You are not Admin!</strong>\n'
                '😜 <em>Get lost</em>'
            )
            await bot.send_message(user_id, msg)
            await state.clear()

    @staticmethod
    async def show_booking_info(message: Message, state: FSMContext, bot: Bot):
        booking_id = message.text
        user_id = message.from_user.id
        try:
            booking_info = await check_booking_info_as(booking_id)
            status = booking_info.get('status')
            rider = booking_info.get('r_username')
            bikes = booking_info.get('bikes')
            date = booking_info.get('date')
            start = booking_info.get('start')
            end = booking_info.get('end')
            is_admin = booking_info.get('f_phone')
            phone = is_admin if is_admin else booking_info.get('phone')
            emoji = get_emoji_for_status(status)
            msg = _(
                '🟢🟢🟢\n\n'
                '<strong>#{id} <em>find successfully!</em>\n\n'
                '👤 Rider: {rider}\n\n'
                '📞 Contact: {phone}\n\n'
                '🏍 Bikes rented: {bikes}\n\n'
                '📆 Booking date: {date}\n\n'
                '🕛 Start time: {start}\n\n'
                '🕜 End time: {end}\n\n'
                'Status: \n\n{emoji} {status}</strong>'
            ).format(
                id=booking_id,
                rider=rider,
                phone=phone,
                bikes=bikes,
                date=date,
                start=start,
                end=end,
                emoji=emoji,
                status=status,
            )
            await bot.send_message(user_id, msg)
            await state.clear()
        except (ObjectDoesNotExist, ValueError):
            kb = CancelKB().place()
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Booking with id #{id} does not exist!</strong>\n\n'
                '<em>Check your spelling and try again</em> ⤵️'
            ).format(id=booking_id)
            await bot.send_message(user_id, msg, reply_markup=kb)
