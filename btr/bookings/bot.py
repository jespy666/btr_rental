import logging

from django.db import IntegrityError
from django.utils.translation import gettext as _
from django.conf import settings
from telegram import Update
from telegram.ext import (ContextTypes, ApplicationBuilder,
                          CommandHandler, MessageHandler, filters,
                          ConversationHandler)

from btr.bookings.db_handlers import (create_user_by_bot_as,
                                      create_booking_by_bot_as,
                                      check_user_exist_as)
from btr.bookings.tasks import send_details
from btr.users.tasks import send_data_from_tg


class BookingBot:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    USERNAME, FIRST_NAME, EMAIL, PHONE_NUMBER = range(4)
    EMAIL_CHECK, BOOK_DATE, BOOK_START_TIME, BOOK_HOURS = range(4)
    ADMIN_CHECK, FOREIGN_PHONE, FOREIGN_START, FOREIGN_END = range(4)

    def __init__(self, token: str):
        self.token = token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Hi! I am BroTeamRacing booking bot\n'
            'There are commands that you can type:\n'
            'To create at account (required for booking): /create\n'
            'To book ride right now: /book\n'
            'To see help - /help\n'
            'By details you can visit our web-site\n'
            'broteamracing.ru\n'
            'or vk-group\n'
            'vk.com/broteamracing'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )

    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        help_text = _(
            'If you have any questions or problems with your booking,'
            ' please contact me at:\n'
            '+7 999 235-00-91\n'
            'Or https://vk.me/broteamracing'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text
        )

    async def create_command(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Let\'s create an account!\n'
            'Please, provide a Username\n'
            '*max length no more 40 symbols:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.USERNAME

    async def ask_username(self, update: Update, context):
        username_text = update.message.text
        context.user_data['username'] = username_text
        username = context.user_data.get('username')
        message = _(
            'Great {username}!\nNow, please provide your first name:'
        ).format(username=username)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.FIRST_NAME

    async def ask_first_name(self, update: Update, context):
        context.user_data['first_name'] = update.message.text
        message = _(
            'Super! Now i need your valid Email:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.EMAIL

    async def ask_email(self, update: Update, context):
        context.user_data['email'] = update.message.text
        message = _(
            'We are almost finished, all that remains is to enter '
            'the phone number:\nPhone number must be in format: +77777777777'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.PHONE_NUMBER

    async def ask_phone_and_create(self, update: Update, context):
        context.user_data['phone_number'] = update.message.text

        collected_data = context.user_data
        try:
            email, name, password = await create_user_by_bot_as(collected_data)
            send_data_from_tg.delay(email, name, password)
            success_message = _(
                'User created successfully!\n'
                'An email with your login information will be sent to {email}'
                'You can track your bookings in your profile on\n'
                'broteamracing.ru'
            ).format(USERNAME=self.USERNAME, email=email)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_message
            )
        except IntegrityError as e:
            error_message = str(e).split(':')[-1].strip()
            error_field = error_message.split('.')[-1].strip()
            error_text = _(
                'Field {error_field} already used, try again!'
                '/create /help'
            ).format(error_field=error_field)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_text
            )
        finally:
            return ConversationHandler.END

    async def book_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Please enter your email to proceed with booking:'
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.EMAIL_CHECK

    async def check_user_and_ask_date(self, update: Update, context):
        email = update.message.text
        if await check_user_exist_as(email):
            context.user_data['user_email'] = email
            success_message = _(
                'User with email {email} find successfully!\n'
                'Please tell me the date you would like to make'
                ' a reservation for\n'
                'in format YYYY-MM-DD:'
            ).format(email=email)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_message,
            )
            return self.BOOK_DATE
        else:
            message = _(
                'Can\'t find user with email {email}(\n'
                'Check your spelling or create a new account:\n'
                '/create\n'
                'Or type a /help command'
            ).format(email=email)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
            return ConversationHandler.END

    async def ask_start_time(self, update: Update, context):
        context.user_data['book_date'] = update.message.text
        message = _(
            'Ok!\nWhat time should you rent?:\n'
            'Please, type in format: HH:MM'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.BOOK_START_TIME

    async def ask_hours(self, update: Update, context):
        context.user_data['book_start_time'] = update.message.text
        date = context.user_data.get('book_date')
        time = context.user_data.get('book_start_time')
        message = _(
            'You will be scheduled for rental on {date}\n'
            'On {time}\n'
            'How long do you plan to ride?\n'
            'Enter the number of hours (example - 1)'
        ).format(date=date, time=time)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.BOOK_HOURS

    async def make_booking(self, update: Update, context):
        context.user_data['book_hours'] = int(update.message.text)
        book_data = context.user_data

        try:
            interval = await create_booking_by_bot_as(book_data)
            date = book_data.get('book_date'),
            start = interval.get('start_time'),
            end = interval.get('end_time'),
            email = book_data.get('user_email')
            message = _(
                'Booking created successfully!\n'
                'Details:\n'
                'Date of ride: {date}\n'
                'Time of ride: from {start} to {end}\n'
                'We have sent you complete booking information by email:\n'
                '{email}'
            ).format(date=date, start=start, end=end, email=email)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
            send_details.delay(email, date, start, end)

        except Exception as e:
            message = f'{str(e)}\n{book_data}'
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
        finally:
            return ConversationHandler.END

    async def admin_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Hi, admin!\n'
            'Confirm admin rights, type a password:\n'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.ADMIN_CHECK

    async def check_admin_and_start_booking(self, update: Update, context):
        password = update.message.text
        if password == settings.TG_ADMIN_PASSWORD:
            message = _(
                'Admin privileges confirmed!\n'
                'Type rider phone number (for example: +70000000000):'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
            return self.FOREIGN_PHONE
        else:
            message = _(
                'Wrong password, try again!\n'
                '/admin'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
            return ConversationHandler.END

    async def ask_admin_date(self, update: Update, context):
        context.user_data['foreign_phone'] = update.message.text
        message = _(
            'Got it!\n'
            'Type a date for client {phone}\n'
            'In format YYYY:MM:DD:'
        ).format(phone=context.user_data.get('foreign_phone'))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        return self.FOREIGN_DATE

    async def ask_admin_start(self, update: Update, context):
        context.user_data['foreign_date'] = update.message.text
        message = _(
            'Ok!\n'
            'Now enter the time of start in format HH:MM:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        return self.FOREIGN_START

    async def ask_admin_end(self, update: Update, context):
        context.user_data['foreign_start'] = update.message.text
        message = _(
            'Ok!\n'
            'Now enter the time of end in format HH:MM:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        return self.FOREIGN_END

    async def make_foreign_book(self, update: Update, context):
        context.user_data['foreign_end'] = update.message.text

    def run(self):
        application = ApplicationBuilder().token(self.token).build()

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help_command)
        create_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('create', self.create_command)
            ],
            states={
                self.USERNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_username)
                ],
                self.FIRST_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_first_name)
                ],
                self.EMAIL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_email)
                ],
                self.PHONE_NUMBER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_phone_and_create)]
            },
            fallbacks=[]
        )

        booking_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('book', self.book_command)
            ],
            states={
                self.EMAIL_CHECK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.check_user_and_ask_date)
                ],
                self.BOOK_DATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_start_time)
                ],
                self.BOOK_START_TIME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_hours)
                ],
                self.BOOK_HOURS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.make_booking)]
            },
            fallbacks=[]
        )

        admin_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('admin', self.admin_command)
            ],
            states={
                self.ADMIN_CHECK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.check_admin_and_start_booking)
                ],
                self.FOREIGN_PHONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_admin_date)
                ],
                self.FOREIGN_START: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_admin_start)
                ],
                self.FOREIGN_END: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.make_booking)]
            },
            fallbacks=[]
        )

        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(create_conv_handler)
        application.add_handler(booking_conv_handler)
        application.add_handler(admin_conv_handler)

        application.run_polling()
