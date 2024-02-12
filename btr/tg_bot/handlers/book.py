from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from ..keyboards.kb_cancel import CancelKB
from ..keyboards.kb_dialog import DialogKB
from ..states.book_ride import BookingState
from ..utils.validators import (validate_email, validate_bike_quantity,
                                validate_date, validate_time,
                                validate_time_range)
from ...orm_utils import check_user_exist_as, SlotsFinder, create_booking_as
from ..utils.exceptions import (InvalidEmailError, WrongBikesCountError,
                                InvalidDateError, DateInPastError,
                                InvalidTimeFormatError,
                                TimeIsNotAvailableError,
                                EndBiggerThenStartError)
from ..utils.handlers import (get_slots_for_bot_view, extract_start_times,
                              check_available_start_time,
                              extract_hours, get_end_time,
                              check_available_hours)
from ...tasks.bookings import send_booking_details


class BookingRide:

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<strong>Make booking</strong>\n\n'
            '<em>To book a new ride, please type your valid email</em>\n\n'
            '⚠️ <strong>Case sensitive</strong> ⤵️'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(BookingState.bookEmail)

    @staticmethod
    async def ask_bikes(message: Message, state: FSMContext, bot: Bot):
        email = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_email(email)
            await check_user_exist_as(email)
            bikes = ['1', '2', '3', '4']
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>User with email <strong>{email}</strong> find '
                'successfully!\n\n'
                'How many bikes should i served?</em>'
            ).format(email=email)
            msg2 = _('<em>Choose available bikes count</em> ⤵️')
            kb_reply = DialogKB(bikes).place()
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
            await state.update_data(email=email, bikes_kb=kb_reply)
            await state.set_state(BookingState.bookBikes)
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
    async def ask_date(message: Message, state: FSMContext, bot: Bot):
        book_data = await state.get_data()
        bikes = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_bike_quantity(bikes)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Ok, i prepared {bikes} bikes to this ride!\n\n'
                'What <strong>date</strong> should I use to book?</em>\n\n'
                '<strong>'
                '📆 Format: YYYY-MM-DD\n\n'
                '⚠️ Type with \'-\' ⤵️'
                '</strong>'
            ).format(bikes=bikes)
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.update_data(bikes=bikes)
            await state.set_state(BookingState.bookDate)
        except WrongBikesCountError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Bikes count must be at <em>1 - 4</em>!\n\n'
                '</strong>'
            )
            msg2 = _(
                '<em>Choose again</em> ⤵️'
            )
            kb_reply = book_data.get('bikes_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)

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
                await state.update_data(
                    date=date,
                    starts_kb=kb_reply,
                    slots=slots_view,
                    slots_list=free_slots,
                )
                await state.set_state(BookingState.bookStart)
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
                '<strong>Invalid date format "{date}"!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            ).format(date=date)
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
        book_data = await state.get_data()
        start = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        slots_list = book_data.get('slots_list')
        slots = book_data.get('slots')
        date = book_data.get('date')
        try:
            validate_time(start)
            check_available_start_time(start, slots_list)
            hours = extract_hours(slots_list, start)
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
            await state.update_data(start=start, hours_kb=kb_reply)
            await state.set_state(BookingState.bookHours)
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n'
                '</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = book_data.get('starts_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 Time {time} is already booked!\n\n'
                '</strong>'
                '<em>Available start times are ↙️</em>\n\n'
                '<strong>{slots}</strong>\n\n'
            ).format(time=start, slots=slots)
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = book_data.get('starts_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)

    @staticmethod
    async def make_booking(message: Message, state: FSMContext, bot: Bot):
        book_data = await state.get_data()
        hours = message.text
        user_id = message.from_user.id
        name = message.from_user.full_name
        kb = CancelKB().place()
        slots_list = book_data.get('slots_list')
        slots = book_data.get('slots')
        bikes = book_data.get('bikes')
        date = book_data.get('date')
        start = book_data.get('start')
        email = book_data.get('email')
        end = get_end_time(start, hours)
        try:
            validate_time(end)
            validate_time_range(start, end)
            check_available_hours(start, hours, slots_list)
            book_data['end'] = end
            booking_id = await create_booking_as(book_data)
            msg = _(
                '🎉🎉🎉\n\n'
                '<strong>Booking created successfully!</strong>\n\n'
                '<em>Book data ↙️\n\n'
                '🆔 Booking id: <strong>#{id}</strong>\n\n'
                '📆 Booking date: <strong>{date}</strong>\n\n'
                '🕛 Start time: <strong>{start}</strong>\n\n'
                '🕜 End time: <strong>{end}</strong>\n\n'
                '⏰ Hours: <strong>{hours}</strong>\n\n'
                '🏍 Bikes: {bikes}\n\n'
                'Booking status ↙️\n\n'
                '🟡 <strong>Pending</strong>\n\n'
                'All booking info was send to ↙️\n\n'
                '{email}\n\n'
                'You can track your booking status on profile page ↙️\n\n'
                'broteamracing.ru</em>'
            ).format(
                id=booking_id,
                date=date,
                start=start,
                end=end,
                hours=hours,
                bikes=bikes,
                email=email,
            )
            await bot.send_message(user_id, msg)
            await state.clear()
            send_booking_details.delay(email, name, date, _('pending'),
                                       start, end, bikes, booking_id)
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = book_data.get('hours_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except EndBiggerThenStartError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>End time must be bigger Start time!\n\n</strong>'
            )
            msg2 = _('<strong>Try again ⤵️</strong>')
            kb_reply = book_data.get('hours_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 This time slot is already booked!\n\n</strong>'
            )
            msg2 = _(
                '<em>Available slots are ↙️\n\n'
                '<strong>{slots}</strong>\n\n'
                '<em>Your start time is: <strong>{start}</strong></em>\n\n'
                '<strong>Try again (choose hours) ⤵️</strong>'
            ).format(slots=slots, start=start)
            kb_reply = book_data.get('hours_kb')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
