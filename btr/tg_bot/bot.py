import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from .utils.commands import set_commands
from .states.create_account import CreateAccountState

from .handlers.start import Start
from .handlers.help import Help
from .handlers.create import CreateAccount


class BookingBot:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    def __init__(self, token: str):
        self.bot = Bot(token=token, parse_mode='HTML')
        self.dp = Dispatcher()

    def setup(self):
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

    async def run(self):
        self.setup()
        await set_commands(self.bot)
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        finally:
            await self.bot.session.close()
