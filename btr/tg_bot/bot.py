import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from .utils.commands import set_commands
from .states.create_account import CreateAccountState
from .states.reset_password import ResetPasswordState
from .states.create_booking import BookingState
from .states.cancel_booking import BookCancelState
from .states.edit_booking import EditBookingState
from .states.admin.foreign_book import ForeignBookingState
from .states.admin.change_status import ChangeStatusState
from .states.admin.check_booking import CheckBookingState

from .handlers.start_message import Start
from .handlers.help_message import Help
from .handlers.prices_message import Prices
from .handlers.create_account import CreateAccount
from .handlers.cancel_dialog import Cancel
from .handlers.reset_password import ResetPassword
from .handlers.create_booking import BookingRide
from .handlers.cancel_booking import CancelRide
from .handlers.edit_booking import EditBooking
from .handlers.admin.foreign_book import ForeignBook
from .handlers.admin.change_status import ChangeStatus
from .handlers.admin.check_booking import CheckBooking


class BookingBot:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    def __init__(self, token: str):
        self.bot = Bot(token=token, parse_mode='HTML')
        self.dp = Dispatcher()

    def _setup(self):
        self.dp.message.register(Start.handle, Command(commands='start'))
        self.dp.message.register(Help.handle, Command(commands='help'))
        self.dp.message.register(Prices.handle, Command(commands='prices'))
        self.dp.message.register(
            CreateAccount.ask_name,
            Command(commands='create'),
        )
        self.dp.message.register(
            CreateAccount.ask_username,
            CreateAccountState.regName,
        )
        self.dp.message.register(
            CreateAccount.ask_email,
            CreateAccountState.regUsername,
        )
        self.dp.message.register(
            CreateAccount.ask_phone,
            CreateAccountState.regEmail,
        )
        self.dp.message.register(
            CreateAccount.create_account,
            CreateAccountState.regPhone,
        )
        self.dp.message.register(
            ResetPassword.ask_email,
            Command(commands='reset'),
        )
        self.dp.message.register(
            ResetPassword.ask_code,
            ResetPasswordState.resetEmail,
        )
        self.dp.message.register(
            ResetPassword.reset_password,
            ResetPasswordState.verificationCode,
        )
        self.dp.message.register(
            BookingRide.ask_email,
            Command(commands='book'),
        )
        self.dp.message.register(
            BookingRide.ask_bikes,
            BookingState.bookEmail,
        )
        self.dp.message.register(
            BookingRide.ask_date,
            BookingState.bookBikes,
        )
        self.dp.message.register(
            BookingRide.ask_start,
            BookingState.bookDate,
        )
        self.dp.message.register(
            BookingRide.ask_hours,
            BookingState.bookStart,
        )
        self.dp.message.register(
            BookingRide.make_booking,
            BookingState.bookHours,
        )
        self.dp.message.register(
            CancelRide.ask_email,
            Command(commands='cancel'),
        )
        self.dp.message.register(
            CancelRide.ask_password,
            BookCancelState.email,
        )
        self.dp.message.register(
            CancelRide.choose_booking,
            BookCancelState.password,
        )
        self.dp.message.register(
            CancelRide.confirm_cancel,
            BookCancelState.pk,
        )
        self.dp.message.register(
            CancelRide.cancel_booking,
            BookCancelState.confirm,
        )
        self.dp.message.register(
            EditBooking.ask_email,
            Command(commands='edit'),
        )
        self.dp.message.register(
            EditBooking.ask_password,
            EditBookingState.email,
        )
        self.dp.message.register(
            EditBooking.choose_booking,
            EditBookingState.password,
        )
        self.dp.message.register(
            EditBooking.ask_start,
            EditBookingState.pk,
        )
        self.dp.message.register(
            EditBooking.ask_hours,
            EditBookingState.start,
        )
        self.dp.message.register(
            EditBooking.ask_bikes,
            EditBookingState.end,
        )
        self.dp.message.register(
            EditBooking.edit_booking,
            EditBookingState.bikes,
        )
        self.dp.message.register(
            ForeignBook.ask_bikes,
            Command(commands='adbook'),
        )
        self.dp.message.register(
            ForeignBook.ask_phone,
            ForeignBookingState.outBikes,
        )
        self.dp.message.register(
            ForeignBook.ask_date,
            ForeignBookingState.outPhone,
        )
        self.dp.message.register(
            ForeignBook.ask_start,
            ForeignBookingState.outDate,
        )
        self.dp.message.register(
            ForeignBook.ask_hours,
            ForeignBookingState.outStart,
        )
        self.dp.message.register(
            ForeignBook.make_booking,
            ForeignBookingState.outHours,
        )
        self.dp.message.register(
            ChangeStatus.ask_id,
            Command(commands='change'),
        )
        self.dp.message.register(
            ChangeStatus.ask_status,
            ChangeStatusState.bookingId,
        )
        self.dp.message.register(
            ChangeStatus.change_status,
            ChangeStatusState.bookingStatus,
        )
        self.dp.message.register(
            CheckBooking.ask_id,
            Command(commands='check'),
        )
        self.dp.message.register(
            CheckBooking.show_booking_info,
            CheckBookingState.bookingId,
        )
        self.dp.callback_query.register(
            Cancel().handle,
            F.data == 'cancel-dialog',
        )
        self.dp.callback_query.register(
            Start().callback_handle,
            F.data == 'start',
        )
        self.dp.callback_query.register(
            Help().callback_handle,
            F.data == 'help',
        )
        self.dp.callback_query.register(
            Prices().callback_handle,
            F.data == 'price',
        )
        self.dp.callback_query.register(
            CreateAccount.ask_name,
            F.data == 'create',
        )
        self.dp.callback_query.register(
            ResetPassword.ask_email,
            F.data == 'reset',
        )
        self.dp.callback_query.register(
            BookingRide.ask_email,
            F.data == 'book',
        )
        self.dp.callback_query.register(
            CancelRide.ask_email,
            F.data == 'cancel',
        )
        self.dp.callback_query.register(
            EditBooking.ask_email,
            F.data == 'edit',
        )

    async def run(self):
        self._setup()
        await set_commands(self.bot)
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        finally:
            await self.bot.session.close()
