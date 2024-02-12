from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _

from btr.orm_utils import SlotsFinder, make_foreign_book_as

from ...states.admin.foreign_book import ForeignBookingState
from ...keyboards.kb_cancel import CancelKB
from ...keyboards.kb_dialog import DialogKB
from ...utils.handlers import (check_admin_access, extract_start_times,
                               check_available_start_time,
                               get_slots_for_bot_view, extract_hours,
                               get_end_time, check_available_hours)
from ...utils.validators import (validate_bike_quantity,
                                 validate_phone_number,
                                 validate_date, validate_time,
                                 validate_time_range)
from ...utils.exceptions import (WrongBikesCountError, InvalidPhoneError,
                                 InvalidDateError, DateInPastError,
                                 InvalidTimeFormatError,
                                 TimeIsNotAvailableError,
                                 EndBiggerThenStartError)


class ForeignBook:

    @staticmethod
    async def ask_bikes(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if check_admin_access(user_id):
            msg = _(
                '🙋🏼‍♂️<em>Hi, <strong>{admin}</strong>!\n'
                'Let\'s book unregistered rider!\n\n'
                '🏍 How many <strong>bikes</strong> do you need?</em>'
            ).format(admin=user_name if user_name else 'Admin')
            msg2 = _(
                '<strong>Choose value</strong> ⤵️'
            )
            bikes = ['1', '2', '3', '4']
            kb_cancel = CancelKB().place()
            kb_reply = DialogKB(bikes).place()
            await bot.send_message(user_id, msg, reply_markup=kb_cancel)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(bikesb=bikes)
            await state.set_state(ForeignBookingState.outBikes)
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
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        bikes = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_bike_quantity(bikes)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Ok! I prepared {bikes} bike(s)\n\n'
                'What phone number should I use to book?</em>\n\n'
                '📝 <strong>Format: +7xxxxxxxxxx</strong>\n\n'
                '⚠️ <strong>Case sensitive</strong> ⤵️'
            ).format(bikes=html.bold(html.quote(bikes)))
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.update_data(bikes=bikes)
            await state.set_state(ForeignBookingState.outPhone)
        except WrongBikesCountError:
            data = await state.get_data()
            bikes_b = data.get('bikesb')
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Bikes count must be at <em>1 - 4</em>!\n\n'
                '</strong>'
            )
            msg2 = _(
                '<em>Choose again</em> ⤵️'
            )
            kb_reply = DialogKB(bikes_b).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)

    @staticmethod
    async def ask_date(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_phone_number(phone)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Got it!\n\n'
                'What <strong>date</strong> should I use to book?</em>\n\n'
                '<strong>'
                '📆 Format: YYYY-MM-DD\n\n'
                '⚠️ Type with \'-\' ⤵️'
                '</strong>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.update_data(phone=phone)
            await state.set_state(ForeignBookingState.outDate)
        except InvalidPhoneError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid phone number format!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(message.from_user.id, msg, reply_markup=kb)

    @staticmethod
    async def ask_start(message: Message, state: FSMContext, bot: Bot):
        date = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            s = SlotsFinder(date)
            free_slots: list = await s.find_available_slots_as()
            if free_slots:
                starts = extract_start_times(free_slots)
                slots_view = get_slots_for_bot_view(free_slots)
                validate_date(date)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Ok! On 📆 {date} available slots is</em> ↙️\n\n'
                    '<strong>{slots}</strong>\n\n'
                ).format(date=date, slots=slots_view)
                msg2 = _(
                    '<strong>Please, choose available start time</strong> ⤵️'
                )
                kb_reply = DialogKB(starts).place()
                await bot.send_message(user_id, msg, reply_markup=kb)
                await bot.send_message(user_id, msg2, reply_markup=kb_reply)
                await state.update_data(date=date, startsb=starts)
                await state.set_state(ForeignBookingState.outStart)
            else:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>On 📆 {date} no available slots!\n\n'
                    '</strong>'
                    '<em>Try again</em> ⤵️'
                ).format(date=date)
                await bot.send_message(user_id, msg, reply_markup=kb)
        except (InvalidDateError, ValidationError, ValueError):
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid date format!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except DateInPastError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Date can\'t be in past!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def ask_hours(message: Message, state: FSMContext, bot: Bot):
        start = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        book_data = await state.get_data()
        free_starts = book_data.get('startsb')
        date = book_data.get('date')
        s = SlotsFinder(date)
        free_slots: list = await s.find_available_slots_as()
        slots_view = get_slots_for_bot_view(free_slots)
        try:
            validate_time(start)
            check_available_start_time(start, free_slots)
            hours = extract_hours(free_slots, start)
            msg = (
                '🟢🟢🟢\n\n'
                '<em>Ok!</em>\n\n'
                '📆 <strong>{date}\n\n'
                '🕒 {start}</strong>\n\n'
            ).format(date=date, start=start)
            msg2 = _('<strong>Choose hours ⤵️</strong>')
            kb_reply = DialogKB(hours).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(start=start, hoursb=hours)
            await state.set_state(ForeignBookingState.outHours)
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n'
                '</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = DialogKB(free_starts).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 Time {time} is already booked!\n\n'
                '</strong>'
                '<em>Available start times are ↙️</em>\n\n'
                '<strong>{slots}</strong>\n\n'
            ).format(time=start, slots=slots_view)
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = DialogKB(free_starts).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)

    @staticmethod
    async def make_booking(message: Message, state: FSMContext, bot: Bot):
        hours = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        book_data = await state.get_data()
        date = book_data.get('date')
        start = book_data.get('start')
        free_hours = book_data.get('hoursb')
        end = get_end_time(start, hours)
        s = SlotsFinder(date)
        free_slots = await s.find_available_slots_as()
        slots_view = get_slots_for_bot_view(free_slots)
        try:
            validate_time(end)
            validate_time_range(start, end)
            check_available_hours(start, hours, free_slots)
            await state.update_data(end=end)
            book_data = await state.get_data()
            await make_foreign_book_as(book_data)
            msg = _(
                '🎉🎉🎉\n\n'
                '<strong>Booking created successfully!</strong>\n\n'
                '<em>Book data ↙️\n\n'
                '📞 Rider contact: <strong>{phone}</strong>\n\n'
                '📆 Booking date: <strong>{date}</strong>\n\n'
                '🕛 Start time: <strong>{start}</strong>\n\n'
                '🕜 End time: <strong>{end}</strong>\n\n'
                '⏰ Hours: <strong>{hours}</strong></em>\n\n'
            ).format(
                phone=book_data.get('phone'),
                date=date,
                start=start,
                end=end,
                hours=hours,
            )
            await bot.send_message(user_id, msg)
            await state.clear()
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = DialogKB(free_hours).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except EndBiggerThenStartError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>End time must be bigger Start time!\n\n</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = DialogKB(free_hours).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 This time slot is already booked!\n\n</strong>'
            ).format(time=end)
            msg2 = _(
                '<em>Available slots are ↙️\n\n'
                '<strong>{slots}</strong>\n\n'
                '<em>Your start time is: <strong>{start}</strong></em>\n\n'
                '<strong>Try again (choose hours) ⤵️</strong>'
            ).format(slots=slots_view, start=start)
            kb_reply = DialogKB(free_hours).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
