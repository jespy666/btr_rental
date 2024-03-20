from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from django.utils.translation import gettext as _

from ..keyboards.kb_cancel import CancelKB
from ..keyboards.kb_dialog import DialogKB
from ..states.edit_booking import EditBookingState
from ..utils.handlers import (extract_start_times, get_slots_for_bot_view,
                              extract_hours, check_available_start_time,
                              get_end_time, check_available_hours, get_hours,
                              json_filter, vk_notify, mail_notify)
from ..utils.validators import (validate_email, validate_pks, validate_time,
                                validate_bike_quantity, validate_time_range,
                                validate_id, validate_hours)
from ...orm_utils import SlotsFinder, AsyncTools
from ..utils.decorators import validators


class EditBooking:
    unchanged_btn = [_('Unchanged'),]

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<em><strong>Edit booking</strong>\n\n'
            'To edit booking, type account email</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(EditBookingState.email)

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
        await state.update_data(email=email, user_info=user_info)
        await state.set_state(EditBookingState.password)

    @staticmethod
    @validators
    async def choose_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        user_info = data.get('user_info')
        password = message.text
        user_id = message.from_user.id
        email = data.get('email')
        kb = CancelKB().place()
        await AsyncTools().check_password(password, email=email)
        username = user_info.get('username')
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
                '<em>Select the booking ID you want to edit ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(pks=bookings_id, ids_kb=kb_reply)
            await state.set_state(EditBookingState.pk)

    @staticmethod
    @validators
    async def ask_start(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        pk = message.text
        validate_id(pk)
        bookings_id = data.get('pks')
        validate_pks(pk, bookings_id)
        booking_info = await AsyncTools().get_booking_info(pk=pk)
        date = booking_info.get('clean_date')
        friendly_date = booking_info.get('friendly_date')
        user_id = message.from_user.id
        kb = CancelKB().place()
        s = SlotsFinder(date)
        email = data.get('email')
        excluded: tuple = await AsyncTools().get_excluded_slot(email, date)
        free_slots: list = await s.find_available_slots_as(
            excluded_slot=excluded
        )
        if free_slots:
            starts = extract_start_times(free_slots)
            starts.append(EditBooking.unchanged_btn[-1])
            slots_view = get_slots_for_bot_view(free_slots)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em><strong>Ok!</strong>\n\n'
                'Available slots on 📆 <strong>{date} ↙️\n\n'
                '{slots}</strong></em>'
            ).format(date=friendly_date, slots=slots_view)
            msg2 = _(
                '<em>Choose available start time from options ⤵️</em>'
            )
            kb_reply = DialogKB(starts).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(
                date=date,
                friendly_date=friendly_date,
                starts_kb=kb_reply,
                slots=slots_view,
                slots_list=free_slots,
                booking_info=booking_info,
                pk=pk,
            )
            await state.set_state(EditBookingState.start)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em>On 📆 <strong>{date}</strong> no available slots!\n\n'
                'Try again ⤵️</em>'
            ).format(date=friendly_date)
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    @validators
    async def ask_hours(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        booking_info = data.get('booking_info')
        canonical_start = booking_info.get('start')
        start_in = message.text
        start = start_in if not start_in == _('Unchanged') else canonical_start
        user_id = message.from_user.id
        kb = CancelKB().place()
        slots_list = data.get('slots_list')
        friendly_date = data.get('friendly_date')
        validate_time(start)
        check_available_start_time(start, slots_list)
        hours = extract_hours(slots_list, start)
        if start == canonical_start:
            hours.append(EditBooking.unchanged_btn[-1])
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Ok!</strong>\n\n'
            'Booking date ➡️  📆 <strong>{date}</strong>\n\n'
            'Start time ➡️  🕒 <strong>{start}</strong></em>'
        ).format(date=friendly_date, start=start)
        msg2 = _('<em>Choose hours from options ⤵️</em>')
        kb_reply = DialogKB(hours).place()
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(start=start, hours_kb=kb_reply)
        await state.set_state(EditBookingState.end)

    @staticmethod
    @validators
    async def ask_bikes(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        booking_info = data.get('booking_info')
        canonical_end = booking_info.get('end')
        user_id = message.from_user.id
        kb = CancelKB().place()
        hours_in = message.text
        start = data.get('start')
        if not hours_in == _('Unchanged'):
            hours = hours_in
            validate_hours(hours)
            end = get_end_time(start, hours)
        else:
            end = canonical_end
            hours = get_hours(start, end)
        bikes = ['1', '2', '3', '4', _('Unchanged')]
        kb_reply = DialogKB(bikes).place()
        slots_list = data.get('slots_list')
        validate_time_range(start, end)
        check_available_hours(start, hours, slots_list)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Ok!</strong>\n'
            'Do you want to change bikes?\n\n'
            '🏍 Requested bikes count: <strong>{bikes}</strong></em>'
        ).format(bikes=booking_info.get('bikes'))
        msg2 = _(
            '<em>Choose bike count if yes, otherwise,\n'
            'press <strong>Unchanged</strong> button ⤵️</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(end=end, bikes_kb=kb_reply, hours=hours)
        await state.set_state(EditBookingState.bikes)

    @staticmethod
    @validators
    async def edit_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        booking_info = data.get('booking_info')
        user_info = data.get('user_info')
        pk = data.get('pk')
        user_id = message.from_user.id
        bikes_in = message.text
        canonical_bikes = booking_info.get('bikes')
        bikes = bikes_in if not bikes_in == _('Unchanged') else canonical_bikes
        validate_bike_quantity(bikes)
        data['bikes'] = bikes
        friendly_date = data.get('friendly_date')
        await AsyncTools().edit_booking(**data)
        data.update(user_info)
        clean_data = json_filter(data)
        clean_data['date'] = friendly_date
        clean_data['pk'] = pk
        clean_data['status'] = _('pending')
        vk_notify(False, False, **clean_data)
        mail_notify('self_booking_edit', **clean_data)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Booking #{pk} successfully edited!</strong>\n\n'
            'Updated booking data ↙️\n\n'
            '🆔 Booking id: <strong>#{pk}</strong>\n\n'
            '📆 Booking date: <strong>{date}</strong>\n\n'
            '🕛 Start time: <strong>{start}</strong>\n\n'
            '🕜 End time: <strong>{end}</strong>\n\n'
            '⏰ Hours: <strong>{hours}</strong>\n\n'
            '🏍 Bikes: <strong>{bikes} bike(s)</strong>\n\n'
            'Booking status ↙️\n\n'
            '🟡 <strong>Pending</strong>\n\n'
            'Updated booking info was sent to ↙️\n\n'
            '<strong>{email}</strong>\n\n'
            'You can manage your bookings on profile page ↙️\n\n'
            '👤 <strong>broteamracing.ru/auth/login</strong></em>'
        ).format(
            pk=pk,
            date=data.get('friendly_date'),
            start=data.get('start'),
            end=data.get('end'),
            hours=data.get('hours'),
            bikes=bikes,
            email=data.get('email'),
        )
        await bot.send_message(user_id, msg)
        await state.clear()
