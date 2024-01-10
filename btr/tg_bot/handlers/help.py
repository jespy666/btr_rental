from aiogram import Bot
from aiogram.types import Message

from django.utils.translation import gettext as _


class Help:

    @staticmethod
    async def handle(message: Message, bot: Bot):
        await bot.send_message(
            message.from_user.id,
            _(
                '<strong>Any issues and questions?</strong>\n'
                '<em>Contact us:</em>\n'
                'vk.me/broteamracing\n\n'
                '<strong>All contacts:</strong>\n\n'
                '📞 <strong>+79992350091</strong> <em>Vladimir</em>\n\n'
                '📞 <strong>+79817850451</strong> <em>Alexander</em>\n\n'
                '🌐 broteamracing.ru\n\n'
                '👥 vk.com/broteamracing\n\n'
            )
        )
