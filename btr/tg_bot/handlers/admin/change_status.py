from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from btr.orm_utils import check_booking_info_as, change_booking_status_as
from btr.tasks.book_tasks import send_booking_notify
from ...utils.handlers import (check_admin_access, get_emoji_for_status,
                               remove_seconds)
from ...keyboards.kb_cancel import CancelKB
from ...keyboards.kb_dialog import DialogKB
from ...states.admin.change_status import ChangeStatusState
from ...utils.exceptions import SameStatusSelectedError


class ChangeStatus:

    @staticmethod
    async def ask_id(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n'
                'Let\'s change booking status!\n\n'
                'Please, tell me booking <strong>id</strong></em> ⤵️'
            ).format(admin=user_name if user_name else 'Admin')
            kb_cancel = CancelKB().place()
            await bot.send_message(user_id, msg, reply_markup=kb_cancel)
            await state.set_state(ChangeStatusState.bookingId)
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
    async def ask_status(message: Message, state: FSMContext, bot: Bot):
        booking_id = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        statuses = [_('confirmed'), _('canceled')]
        try:
            booking_info = await check_booking_info_as(booking_id)
            date = booking_info.get('date')
            start = remove_seconds(booking_info.get('start'))
            end = remove_seconds(booking_info.get('end'))
            status = booking_info.get('status')
            is_admin = booking_info.get('f_phone')
            phone = is_admin if is_admin else booking_info.get('phone')
            emoji = get_emoji_for_status(status)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Booking status with id </em><strong>#{id}:\n\n'
                '{emoji} {status}</strong>\n\n'
                '<em>Full booking details</em> ↙️\n\n'
                '<strong>📆 Booking date: {date}\n\n'
                '🕛 Start time: {start}\n\n'
                '🕜 End time: {end}\n\n'
                '📞 Client phone: {phone}</strong>\n\n'
            ).format(
                emoji=emoji,
                id=booking_id,
                status=status,
                date=date,
                start=start,
                end=end,
                phone=phone
            )
            msg2 = _(
                '<em>Choose new status for booking</em><strong> #{id} ⤵️'
                '</strong>'
            ).format(id=booking_id)
            kb_reply = DialogKB(statuses).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(bookid=booking_id, statuses=statuses)
            await state.set_state(ChangeStatusState.bookingStatus)
        except ObjectDoesNotExist:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Booking with id #{id} does not exist!</strong>\n\n'
                '<em>Check your spelling and try again</em> ⤵️'
            ).format(id=booking_id)
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def change_status(message: Message, state: FSMContext, bot: Bot):
        status = message.text
        user_id = message.from_user.id
        context = await state.get_data()
        booking_id = context.get('bookid')
        try:
            old_status = await change_booking_status_as(booking_id, status)
            old_emoji = get_emoji_for_status(old_status)
            emoji = get_emoji_for_status(status)
            msg = _(
                '🎉🎉🎉\n\n'
                '<em>Status for id <strong>#{id}</strong> changed'
                ' successfully!</em><strong>\n\n'
                'Old status: {old_e} {old_s}\n\n'
                'New status: {new_e} {new_s}</strong>'
            ).format(
                id=booking_id,
                old_e=old_emoji,
                old_s=old_status,
                new_e=emoji,
                new_s=status
            )
            await bot.send_message(user_id, msg)
            await state.clear()
        except SameStatusSelectedError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>You choose the same status!</strong>\n\n'
            )
            msg2 = _('<em>Try again ⤵️</em>')
            kb = CancelKB().place()
            kb_reply = DialogKB(context.get('statuses')).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
