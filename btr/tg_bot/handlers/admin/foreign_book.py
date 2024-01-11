from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html

from django.utils.translation import gettext as _

from btr.orm_utils import SlotsFinder, make_foreign_book_as

from ...states.admin.foreign_book import ForeignBookingState
from ...keyboards.kb_cancel import InlineCancelKB
from ...keyboards.kb_start_time import StartTimesKB
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
            bikes = ['1', '2', '3', '4']
            await bot.answer_callback_query('sss')
            await message.reply(
                msg,
                reply_markup=StartTimesKB(bikes).place_outline()
            )
            await state.set_state(ForeignBookingState.outBikes)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>ACCESS DENIED!\n'
                'You are not Admin!</strong>\n'
                '😜 <em>Get lost</em>'
            )
            await bot.send_message(message.from_user.id, msg)
            await state.clear()

    @staticmethod
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        bikes = message.text
        try:
            validate_bike_quantity(bikes)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Ok! I prepared {bikes} Bikes\n\n'
                'What phone number should I use to book?</em>'
                '📝 <strong>Format: +7xxxxxxxxxx</strong>\n\n'
                '⚠️ <strong>Case sensitive</strong> ⤵️'
            ).format(bikes=html.bold(html.quote(bikes)))
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
            await state.update_data(outbikes=bikes)
            await state.set_state(ForeignBookingState.outPhone)
        except WrongBikesCountError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Bikes count must be at <em>1 - 4</em>!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )

    @staticmethod
    async def ask_date(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        try:
            validate_phone_number(phone)
            msg = _(
                '🟢🟢🟢\n\n'
                '<em>Got it!\n\n'
                'What <strong>date</strong> should I use to book?</em>\n\n'
                '<strong>'
                '📆 Format: YYYY:MM:DD\n\n'
                '⚠️ Type with \':\' ⤵️'
                '</strong>'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
            await state.update_data(outphone=phone)
            await state.set_state(ForeignBookingState.outDate)
        except InvalidPhoneError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid phone number format!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )

    @staticmethod
    async def ask_start(message: Message, state: FSMContext, bot: Bot):
        date = message.text
        s = SlotsFinder(date)
        free_slots: list = await s.find_available_slots_as()
        if free_slots:
            starts = extract_start_times(free_slots)
            slots_view = get_slots_for_bot_view(free_slots)
            try:
                validate_date(date)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Ok! On 📆 {date} available slots is</em> ↙️\n\n'
                    '<strong>{slots}</strong>\n\n'
                    '<em>Please, choose available start time</em> ⤵️'
                ).format(date=date, slots=slots_view)
                kb_cancel = StartTimesKB().place()
                kb_starts = StartTimesKB().place_outline(starts)
                await bot.send_message(
                    message.from_user.id,
                    msg,
                    reply_markup=kb_cancel,
                )
                await bot.send_message(
                    message.from_user.id,
                    msg,
                    reply_markup=kb_starts,
                )
                await state.update_data(outdate=date)
                await state.set_state(ForeignBookingState.outStart)
            except InvalidDateError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Invalid date format!\n\n'
                    '</strong>'
                    '<em>Try again</em> ⤵️'
                )
                await bot.send_message(
                    message.from_user.id,
                    msg,
                    reply_markup=InlineCancelKB().place(),
                )
            except DateInPastError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Date can\'t be in past!\n\n'
                    '</strong>'
                    '<em>Try again</em> ⤵️'
                )
                await bot.send_message(
                    message.from_user.id,
                    msg,
                    reply_markup=InlineCancelKB().place(),
                )
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>On 📆 {date} no available slots!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            ).format(date=date)
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )

    @staticmethod
    async def ask_hours(message: Message, state: FSMContext, bot: Bot):
        start = message.text
        book_data = await state.get_data()
        date = book_data.get('outdate')
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
                '<em>How many hours?</em> ⤵️'
            ).format(date=date, start=start)
            kb_cancel = StartTimesKB().place()
            kb_hours = StartTimesKB().place_outline(hours)
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=kb_cancel,
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=kb_hours,
            )
            await state.update_data(outstart=start)
            await state.set_state(ForeignBookingState.outHours)
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 Time {time} is already booked!\n\n'
                '</strong>'
                '<em>Available start times are ↙️\n\n'
                '<strong>{slots}</strong>\n\n'
                'Try again</em> ⤵️'
            ).format(time=start, slots=slots_view)
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )

    @staticmethod
    async def make_booking(message: Message, state: FSMContext, bot: Bot):
        hours = message.text
        book_data = await state.get_data()
        date = book_data.get('outdate')
        start = book_data.get('outstart')
        end = get_end_time(start, hours)
        s = SlotsFinder(date)
        free_slots = await s.find_available_slots_as()
        slots_view = get_slots_for_bot_view(free_slots)
        try:
            validate_time(end)
            validate_time_range(start, end)
            check_available_hours(start, hours, free_slots)
            await state.update_data(outend=end)
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
                    '⏰ Hours: <strong>{hours} hours</strong></em>\n\n'
                ).format(
                phone=book_data.get('outphone'),
                date=date,
                start=start,
                end=end,
                hours=hours,
            )
            await bot.send_message(message.from_user.id, msg)
            await state.clear()
        except InvalidTimeFormatError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Invalid time format!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
        except EndBiggerThenStartError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>End time must be bigger then Start time!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
        except TimeIsNotAvailableError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>🕒 Time {time} is already booked!\n\n'
                '</strong>'
                '<em>Available start times are ↙️\n\n'
                '<strong>{slots}</strong>\n\n'
                'Try again</em> ⤵️'
            ).format(time=end, slots=slots_view)
            await bot.send_message(
                message.from_user.id,
                msg,
                reply_markup=InlineCancelKB().place(),
            )
