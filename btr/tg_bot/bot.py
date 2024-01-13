import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from .utils.commands import set_commands
from .states.create_account import CreateAccountState
from .states.admin.foreign_book import ForeignBookingState
from .states.admin.change_status import ChangeStatusState
from .states.admin.check_booking import CheckBookingState

from .handlers.start import Start
from .handlers.help import Help
from .handlers.create import CreateAccount
from .handlers.cancel import Cancel
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
            F.data == 'cancel',
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
            CreateAccount.ask_name,
            F.data == 'create',
        )

    async def run(self):
        self._setup()
        await set_commands(self.bot)
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        finally:
            await self.bot.session.close()
