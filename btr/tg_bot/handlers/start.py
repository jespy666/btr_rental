from aiogram import Bot
from aiogram.types import Message

from django.utils.translation import gettext as _


class Start:

    @staticmethod
    async def handle(message: Message, bot: Bot):
        await bot.send_message(
            message.from_user.id,
            _(
                '<strong>16+❗️</strong>\n\n'
                '<em>Hi!\nI\'m BroTeamRacing Bot!\n'
                'With my help, you\'ll be able to:</em>\n\n'
                '👤 <strong>Quick Sign Up</strong>\n\n'
                '📆 <strong>Make Bookings</strong>\n\n'
                '🔓 <strong>Reset your password</strong>\n\n'
                '📱 <strong>Get our contacts</strong>\n'
            )
        )
