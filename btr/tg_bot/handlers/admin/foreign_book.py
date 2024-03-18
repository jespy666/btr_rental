from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html

from django.utils.translation import gettext as _

from btr.orm_utils import SlotsFinder, AsyncTools
from ...states.admin.foreign_book import ForeignBookingState
from ...keyboards.kb_cancel import CancelKB
from ...keyboards.kb_dialog import DialogKB
from ...utils.decorators import validators
from ...utils.handlers import (check_admin_access, extract_start_times,
                               check_available_start_time,
                               get_slots_for_bot_view, extract_hours,
                               get_end_time, check_available_hours,
                               friendly_formatted_date, json_filter, vk_notify)
from ...utils.validators import (validate_bike_quantity,
                                 validate_phone_number,
                                 validate_date, validate_time,
                                 validate_time_range, validate_hours)


class ForeignBook:

    @staticmethod
    async def ask_bikes(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n\n'
                'Let\'s book unregistered rider!\n\n'
                '🏍 How many <strong>bikes</strong> do you need?</em>'
            ).format(admin=user_name if user_name else 'Admin')
            msg2 = _(
                '<em>Choose value from options⤵️</em>'
            )
            bikes = ['1', '2', '3', '4']
            kb_cancel = CancelKB().place()
            kb_reply = DialogKB(bikes).place()
            await bot.send_message(user_id, msg, reply_markup=kb_cancel)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(bikes_kb=kb_reply)
            await state.set_state(ForeignBookingState.outBikes)
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
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        bikes = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_bike_quantity(bikes)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em>Ok! I prepared <strong>{bikes} bike(s)</strong>\n\n'
            'What phone number should I use to book?\n\n'
            '📝 <strong>Format: +7XXXXXXXXXX</strong></em>\n\n'
        ).format(bikes=html.bold(html.quote(bikes)))
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(bikes=bikes)
        await state.set_state(ForeignBookingState.outPhone)

    @staticmethod
    @validators
    async def ask_date(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_phone_number(phone)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Got it!</strong>\n\n'
            'What <strong>date</strong> should I use to book?\n\n'
            '<strong>📆 Format: YYYY-MM-DD\n\n⚠️ Type with \'-\' ⤵️'
            '</strong></em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(phone=phone)
        await state.set_state(ForeignBookingState.outDate)

    @staticmethod
    @validators
    async def ask_start(message: Message, state: FSMContext, bot: Bot):
        date = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_date(date)
        friendly_date = AsyncTools().get_friendly_date(
            friendly_formatted_date(date)
        )
        s = SlotsFinder(date)
        free_slots: list = await s.find_available_slots_as()
        if free_slots:
            starts = extract_start_times(free_slots)
            kb_reply = DialogKB(starts).place()
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
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(
                date=date,
                starts_kb=kb_reply,
                slots=slots_view,
                friendly_date=friendly_date
            )
            await state.set_state(ForeignBookingState.outStart)
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
        start = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        data = await state.get_data()
        date = data.get('date')
        validate_time(start)
        s = SlotsFinder(date)
        free_slots: list = await s.find_available_slots_as()
        check_available_start_time(start, free_slots)
        hours = extract_hours(free_slots, start)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Ok!</strong>\n\n'
            'Booking date ➡️  📆 <strong>{date}</strong>\n\n'
            'Start time ➡️  🕒 <strong>{start}</strong></em>'
        ).format(date=data.get('friendly_date'), start=start)
        msg2 = _('<em>Choose hours from options ⤵️</em>')
        kb_reply = DialogKB(hours).place()
        await bot.send_message(user_id, msg, reply_markup=kb)
        await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        await state.update_data(start=start, hours_kb=kb_reply)
        await state.set_state(ForeignBookingState.outHours)

    @staticmethod
    @validators
    async def make_booking(message: Message, state: FSMContext, bot: Bot):
        hours = message.text
        validate_hours(hours)
        user_id = message.from_user.id
        data = await state.get_data()
        date = data.get('date')
        friendly_date = data.get('friendly_date')
        start = data.get('start')
        end = get_end_time(start, hours)
        s = SlotsFinder(date)
        free_slots = await s.find_available_slots_as()
        validate_time_range(start, end)
        check_available_hours(start, hours, free_slots)
        admin = await AsyncTools().get_user_info(username='admin')
        data['end'] = end
        data['pk'] = admin.get('pk')
        pk = await AsyncTools().make_booking(data, is_admin=True)
        clean_data = json_filter(data)
        clean_data['pk'] = pk
        clean_data['date'] = friendly_date
        clean_data['username'] = 'admin'
        vk_notify(True, True, **clean_data)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Booking created successfully!</strong>\n\n'
            'Book data ↙️\n\n'
            '📞 Rider contact: <strong>{phone}</strong>\n\n'
            '📆 Booking date: <strong>{date}</strong>\n\n'
            '🕛 Start time: <strong>{start}</strong>\n\n'
            '🕜 End time: <strong>{end}</strong>\n\n'
            '⏰ Hours: <strong>{hours}</strong></em>'
        ).format(
            phone=data.get('phone'),
            date=friendly_date,
            start=start,
            end=end,
            hours=hours,
        )
        await bot.send_message(user_id, msg)
        await state.clear()
