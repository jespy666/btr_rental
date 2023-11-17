from django.core.management.base import BaseCommand
from django.conf import settings

from btr.bookings.bot import BookingBot


class Command(BaseCommand):
    help = 'Command for run booking tg bot'

    def handle(self, *args, **options):
        bot = BookingBot(settings.TG_BOT_TOKEN)
        bot.run()
