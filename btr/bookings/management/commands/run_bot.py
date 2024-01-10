from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio

from btr.tg_bot.bot import BookingBot


class Command(BaseCommand):

    help = 'Command for run booking tg bot'

    def handle(self, *args, **options):
        bot = BookingBot(settings.TG_BOT_TOKEN)
        asyncio.run(bot.run())
