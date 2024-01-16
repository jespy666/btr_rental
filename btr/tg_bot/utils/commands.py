from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from django.utils.translation import gettext as _


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description=_('Main menu'),
        ),
        BotCommand(
            command='prices',
            description=_('Prices for bikes'),
        ),
        BotCommand(
            command='help',
            description=_('Help message'),
        ),
        BotCommand(
            command='create',
            description=_('Create account'),
        ),
        BotCommand(
            command='book',
            description=_('Make booking (Account required)'),
        ),
        BotCommand(
            command='reset',
            description=_('Reset your forgotten password'),
        ),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
