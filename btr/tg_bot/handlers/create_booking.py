from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.utils.translation import gettext as _

from ..keyboards.kb_cancel import CancelKB
from ..keyboards.kb_dialog import DialogKB
from ..states.create_booking import BookingState
from ..utils.validators import (validate_email, validate_bike_quantity,
                                validate_date, validate_time,
                                validate_time_range)
from ..utils.decorators import validators
from ...orm_utils import AsyncTools, SlotsFinder
from ..utils.handlers import (get_slots_for_bot_view, extract_start_times,
                              check_available_start_time,
                              extract_hours, get_end_time,
                              check_available_hours, vk_notify, json_filter,
                              mail_notify, friendly_formatted_date)


class BookingRide:

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<em><strong>Booking create</strong>\n\n'
            'To book a new ride,\n'
            'type email from your account ⤵️</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(BookingState.bookEmail)

    @staticmethod
    @validators
    async def ask_bikes(message: Message, state: FSMContext, bot: Bot):
        email = message.text.lower()
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_email(email)
        user_info = await AsyncTools().get_user_info(email=email)
        bikes = ['1', '2', '3', '4']
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>User with email <strong>{email}</strong>\n'
            'find successfully!\n\n'
            'How many bikes should i served?</em>'
        ).format(email=email)
        msg2 = _('<em>Choose bikes from options ⤵️</em>')
        kb_reply = DialogKB(bikes).place()
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(email=email, bikes_kb=kb_reply,
                                user_info=user_info)
        await state.set_state(BookingState.bookBikes)

    @staticmethod
    @validators
    async def ask_date(message: Message, state: FSMContext, bot: Bot):
        bikes = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_bike_quantity(bikes)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>Ok, i prepared <strong>{bikes} bike(s)</strong> for ride!\n\n'
            'What <strong>date</strong> should I use to book?\n\n'
            '<strong>📆 Format: YYYY-MM-DD\n\n⚠️ Type with \'-\' ⤵️'
            '</strong></em>'
        ).format(bikes=bikes)
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(bikes=bikes)
        await state.set_state(BookingState.bookDate)

    @staticmethod
    @validators
    async def ask_start(message: Message, state: FSMContext, bot: Bot):
        date = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_date(date)
        s = SlotsFinder(date)
        free_slots: list = await s.find_available_slots_as()
        friendly_date = AsyncTools().get_friendly_date(
            friendly_formatted_date(date)
        )
        if free_slots:
            starts = extract_start_times(free_slots)
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
            )
            await state.set_state(BookingState.bookStart)
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
        start = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        slots_list = data.get('slots_list')
        validate_time(start)
        check_available_start_time(start, slots_list)
        hours = extract_hours(slots_list, start)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Ok!</strong>\n\n'
            'Booking date ➡️  📆 <strong>{date}</strong>\n\n'
            'Start time ➡️  🕒 <strong>{start}</strong></em>'
        ).format(date=data.get('friendly_date'), start=start)
        msg2 = _('<strong>Choose hours ⤵️</strong>')
        kb_reply = DialogKB(hours).place()
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(start=start, hours_kb=kb_reply)
        await state.set_state(BookingState.bookHours)

    @staticmethod
    @validators
    async def make_booking(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        hours = message.text
        user_id = message.from_user.id
        name = message.from_user.full_name
        slots_list = data.get('slots_list')
        start = data.get('start')
        friendly_date = data.get('friendly_date')
        end = get_end_time(start, hours)
        validate_time_range(start, end)
        check_available_hours(start, hours, slots_list)
        data['end'] = end
        data['name'] = name
        user_info = data.get('user_info')
        data.update(user_info)
        data['status'] = _('pending')
        data['pk'] = await AsyncTools().make_booking(data)
        clean_data = json_filter(data)
        clean_data['date'] = friendly_date
        vk_notify(False, True, **clean_data)
        mail_notify('booking_details', **clean_data)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Booking created successfully!</strong>\n\n'
            'Book data ↙️\n\n'
            '🆔 Booking id: <strong>#{pk}</strong>\n\n'
            '📆 Booking date: <strong>{date}</strong>\n\n'
            '🕛 Start time: <strong>{start}</strong>\n\n'
            '🕜 End time: <strong>{end}</strong>\n\n'
            '⏰ Hours: <strong>{hours}</strong>\n\n'
            '🏍 Bikes: <strong>{bikes} bike(s)</strong>\n\n'
            'Booking status ↙️\n\n'
            '🟡 <strong>Pending</strong>\n\n'
            'All booking info was send to ↙️\n\n'
            '<strong>{email}</strong>\n\n'
            'You can manage your bookings on profile page ↙️\n\n'
            '👤 <strong>broteamracing.ru/auth/login</strong></em>'
        ).format(
            pk=data.get('pk'),
            date=friendly_date,
            start=start,
            end=end,
            hours=hours,
            bikes=data.get('bikes'),
            email=data.get('email'),
        )
        await bot.send_message(user_id, msg)
        await state.clear()
