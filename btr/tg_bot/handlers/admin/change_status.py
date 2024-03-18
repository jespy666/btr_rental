from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from django.utils.translation import gettext as _

from btr.orm_utils import AsyncTools
from ...utils.handlers import check_admin_access, get_emoji_for_status, \
    json_filter, vk_notify, mail_notify
from ...keyboards.kb_cancel import CancelKB
from ...keyboards.kb_dialog import DialogKB
from ...states.admin.change_status import ChangeStatusState
from ...utils.decorators import validators
from ...utils.validators import validate_id, validate_status


class ChangeStatus:

    @staticmethod
    async def ask_id(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        kb = CancelKB().place()
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n\n'
                'Let\'s change booking status!\n\n'
                'Please, tell me booking <strong>#ID</strong></em> ⤵️'
            ).format(admin=user_name if user_name else 'Admin')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.set_state(ChangeStatusState.bookingId)
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
    async def ask_status(message: Message, state: FSMContext, bot: Bot):
        pk = message.text
        validate_id(pk)
        user_id = message.from_user.id
        kb = CancelKB().place()
        booking_info = await AsyncTools().get_booking_info(
            load_prefetch='rider', pk=pk)
        changeable_status = await AsyncTools().get_available_status(pk=pk)
        kb_reply = DialogKB([str(changeable_status),]).place()
        status = booking_info.get('status')
        is_admin = booking_info.get('f_phone')
        rider_id = booking_info.get('rider_id')
        user_info = await AsyncTools().get_user_info(pk=rider_id)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>Booking status with id <strong>#{id}</strong> ↙️\n\n'
            '{emoji} <strong>{status}</strong>\n\n'
            'Full booking details ↙️\n\n'
            '📆 Booking date: <strong>{date}</strong>\n\n'
            '🕛 Start time: <strong>{start}</strong>\n\n'
            '🕜 End time: <strong>{end}</strong>\n\n'
            '📞 Client phone: <strong>{phone}</strong></em>\n\n'
        ).format(
            emoji=get_emoji_for_status(status),
            id=pk,
            status=status,
            date=booking_info.get('friendly_date'),
            start=booking_info.get('start'),
            end=booking_info.get('end'),
            phone=is_admin if is_admin else user_info.get('phone'),
        )
        msg2 = _(
            '<em>Choose new status for booking <strong>#{id}</strong> ⤵️</em>'
        ).format(id=pk)
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(pk=pk, status_kb=kb_reply,
                                booking_info=booking_info, user_info=user_info)
        await state.set_state(ChangeStatusState.bookingStatus)

    @staticmethod
    @validators
    async def change_status(message: Message, state: FSMContext, bot: Bot):
        status = message.text
        validate_status(status)
        user_id = message.from_user.id
        data = await state.get_data()
        booking_info = data.get('booking_info')
        user_info = data.get('user_info')
        pk = data.get('pk')
        old_status = booking_info.get('status')
        await AsyncTools().change_booking_status(status, pk)
        clean_data = json_filter(data)
        clean_data.update(booking_info)
        clean_data.update(user_info)
        clean_data['pk'] = pk
        clean_data['status'] = status
        clean_data['date'] = booking_info.get('friendly_date')
        vk_notify(True, False, **clean_data)
        action = 'confirm_msg' if status == _('confirmed') else 'cancel_msg'
        mail_notify(action, **clean_data)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Status for #{id} changed successfully!</strong>\n\n'
            'Old status: {old_emoji} <strong>{old_status}</strong>\n\n'
            'New status: {new_emoji} <strong>{new_status}</strong></em>'
        ).format(
            id=pk,
            old_emoji=get_emoji_for_status(old_status),
            old_status=old_status,
            new_emoji=get_emoji_for_status(status),
            new_status=status,
        )
        await bot.send_message(user_id, msg)
        await state.clear()
