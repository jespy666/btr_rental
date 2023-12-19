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
                                      check_user_exist_as,
                                      create_booking_by_admin_as)
from btr.bookings.tasks import send_details
from btr.bookings.bot_validators import validate_bike_quantity, \
    validate_phone_number, validate_date, validate_time, validate_time_range, \
    validate_email
from btr.users.tasks import send_data_from_tg


class BookingBot:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    USERNAME, FIRST_NAME, EMAIL, PHONE_NUMBER = range(4)
    EMAIL_CHECK, BIKE_COUNT, BOOK_DATE, BOOK_START_TIME, BOOK_HOURS = range(5)
    (ADMIN_CHECK, BIKES_NUM, FOREIGN_PHONE,
     FOREIGN_DATE, FOREIGN_START, FOREIGN_END) = range(6)

    def __init__(self, token: str):
        self.token = token

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Hi! I am BroTeamRacing booking bot\n'
            'There are commands that you can type:\n'
            'To create an account (required for booking): /create\n'
            'To book ride right now: /book\n'
            'To see help message: /help\n'
            'By details you can visit our web-site:\n'
            'broteamracing.ru\n'
            'or vk-group:\n'
            'vk.com/broteamracing'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = _(
            'If you have any questions or problems with your booking,'
            ' please contact me at:\n'
            '+7 999 235-00-91\n'
            'Or\nhttps://vk.me/broteamracing'
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
            'Great {username}!\n'
            'Now, please provide your first name:'
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
            'the phone number:\n'
            'Phone number must be in format: +7 (XXX) XXX-XX-XX'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.PHONE_NUMBER

    async def ask_phone_and_create(self, update: Update, context):
        context.user_data['phone_number'] = update.message.text

        collected_data = context.user_data
        message = ''
        try:
            email, name, password = await create_user_by_bot_as(collected_data)
            send_data_from_tg.delay(email, name, password)
            message = _(
                'User created successfully!\n'
                'An email with your login information will be sent to {email}'
                '\nYou can track your bookings in your profile on\n'
                'broteamracing.ru'
            ).format(USERNAME=self.USERNAME, email=email)

        except IntegrityError as e:
            error_message = str(e).split(':')[-1].strip()
            error_field = error_message.split('.')[-1].strip()
            message = _(
                'Field {error_field} already used, try again!\n'
                '/create /help'
            ).format(error_field=error_field)

        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
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

    async def check_user_and_ask_bike_count(self, update: Update, context):
        email = update.message.text
        message = ''
        try:
            await check_user_exist_as(email)
            validate_email(email)
            context.user_data['user_email'] = email
            message = _(
                'User with email {email} find successfully!\n'
                'Please tell me, how many bikes you want to rent?\n'
                'Min: 1, Max: 4'
            ).format(email=email)
            return self.BIKE_COUNT
        except ValueError:
            message = _(
                'Invalid email format: {email}!\n'
                'Check your spelling and try again:'
            ).format(email=email)
        except NameError:
            message = _(
                'Can\'t find user with email {email} :(\n'
                'Check your spelling or create a new account: /create\n'
                'Type a help command: /help\n'
                'Or try again:'
            ).format(email=email)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_date(self, update: Update, context):
        bike_count = update.message.text
        message = ''
        try:
            validate_bike_quantity(bike_count)
            context.user_data['bike_count'] = bike_count
            message = _(
                'Ok! You are served {bike_count} bikes in this ride.'
                'Now please tell me the date you would like to make'
                ' a reservation for\n'
                'in format YYYY-MM-DD:'
            ).format(bike_count=bike_count)
            return self.BOOK_DATE
        except ValueError:
            message = _(
                'Invalid bikes rental count: {bike_count}!\n'
                'Bikes count must be at 1-4\n'
                'Try again!'
            ).format(bike_count=bike_count)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_start_time(self, update: Update, context):
        date = update.message.text
        message = ''
        try:
            validate_date(date)
            context.user_data['book_date'] = date
            message = _(
                'Ok!\n'
                'What time should you rent?:\n'
                'Please, type in format: HH:MM'
            )
            return self.BOOK_START_TIME
        except ValueError:
            message = _(
                'Invalid date format: {date}!\n'
                'Date format must be: YYYY-MM-DD (with "-")\n'
                'Try again!'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    async def ask_hours(self, update: Update, context):
        start = update.message.text
        message = ''
        try:
            validate_time(start)
            context.user_data['book_start_time'] = start
            date = context.user_data.get('book_date')
            message = _(
                'You will be scheduled for rental on {date}\n'
                'On {time}\n'
                'How long do you plan to ride?\n'
                'Enter the number of hours (example: 3):'
            ).format(date=date, time=start)
            return self.BOOK_HOURS
        except ValueError:
            message = _(
                'Invalid time format: {start}!\n'
                'Correct format is: HH:MM\n'
                'Try again!'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    @staticmethod
    async def make_booking(update: Update, context):
        hours = update.message.text
        context.user_data['book_hours'] = hours
        book_data = context.user_data
        message = ''
        try:
            interval = await create_booking_by_bot_as(book_data)
            date = book_data.get('book_date')
            start = interval.get('start_time')
            end = interval.get('end_time')
            validate_time_range(start, end)
            email = book_data.get('user_email')
            bike_count = book_data.get('book_count')
            message = _(
                'Booking created successfully!\n'
                'Details:\n'
                'Date of ride: {date}\n'
                'Time of ride: from {start} to {end}\n'
                'Number of bikes in the booking: {bike_count}\n'
                'We have sent you complete booking information by email:\n'
                '{email}'
            ).format(date=date, start=start, end=end,
                     bike_count=bike_count, email=email)
            send_details.delay(email, date, start, end, bike_count)
        except ValueError:
            message = _(
                'Invalid end time'
            )
        except Exception as e:
            message = str(e)

        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
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

    async def check_admin_and_ask_bikes_num(self, update: Update, context):
        password = update.message.text
        if password == settings.TG_ADMIN_PASSWORD:
            message = _(
                'Admin privileges confirmed!\n'
                'How many bikes should i rent?\n'
                'Min: 1, Max: 4'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
            return self.BIKES_NUM
        else:
            message = _(
                'Wrong password, try again!\n'
                '/admin'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )
            # return ConversationHandler.END

    async def ask_foreign_phone(self, update: Update, context):
        bikes_num = update.message.text
        message = ''
        try:
            validate_bike_quantity(bikes_num)
            context.user_data['bikes_num'] = update.message.text
            message = _(
                'Ok!\n'
                'Type rider phone number (for example: +71234567890):'
            )
            return self.FOREIGN_PHONE
        except ValueError:
            message = _(
                'Bike count {bikes_num} is invalid!\n'
                'The valid counter is at 1-4!\n'
                'Try again'
            ).format(bikes_num=bikes_num)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_admin_date(self, update: Update, context):
        foreign_phone = update.message.text
        message = ''
        try:
            validate_phone_number(foreign_phone)
            context.user_data['foreign_phone'] = foreign_phone
            message = _(
                'Got it!\n'
                'Type a date for client: {phone}\n'
                'In format YYYY-MM-DD:'
            ).format(phone=context.user_data.get('foreign_phone'))
            return self.FOREIGN_DATE
        except ValueError:
            message = _(
                'Invalid phone number: {phone}!\n'
                'Phone number format must be: +71234567890\n'
                'Try again!'
            ).format(phone=foreign_phone)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_admin_start(self, update: Update, context):
        foreign_date = update.message.text
        message = ''
        try:
            validate_date(foreign_date)
            context.user_data['foreign_date'] = foreign_date
            message = _(
                'Ok!\n'
                'Now enter the time of start in format HH:MM:'
            )
            return self.FOREIGN_START
        except ValueError:
            message = _(
                'Invalid date format: {date}!\n'
                'Date format must be: YYYY-MM-DD (with "-")\n'
                'Try again!'
            ).format(date=foreign_date)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_admin_end(self, update: Update, context):
        start = update.message.text
        message = ''
        try:
            validate_time(start)
            context.user_data['foreign_start'] = start
            message = _(
                'Ok!\n'
                'Now enter the time of end in format HH:MM:'
            )
            return self.FOREIGN_END
        except ValueError:
            message = _(
                'Invalid time format: {start}!\n'
                'Time format must be: HH:MM (with ":")\n'
                'Try again!'
            ).format(start=start)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    @staticmethod
    async def make_foreign_book(update: Update, context):
        start = context.user_data.get('foreign_start')
        end = update.message.text
        message = ''
        try:
            validate_time(end)
            validate_time_range(start, end)
            context.user_data['foreign_end'] = end
            book_data = context.user_data
            await create_booking_by_admin_as(book_data)
            message = _(
                'Booking created successfully!\n'
                'Details:\n'
                'Bikes rented: {bikes_num}\n'
                'Client\'s phone: {phone}\n'
                'Date: {date}\n'
                'From {start} to {end}'
            ).format(
                bikes_num=book_data.get('bikes_num'),
                phone=book_data.get('foreign_phone'),
                date=book_data.get('foreign_date'),
                start=book_data.get('foreign_start'),
                end=book_data.get('foreign_end'),
            )
            return ConversationHandler.END
        except ValueError:
            message = _(
                'End time must be greater than Start time!\n'
                'Your Start: {start}\n'
                'Your End: {end}\n'
                'Try again!'
            ).format(start=start, end=end)
        except Exception as e:
            message = str(e)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

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
                                   self.check_user_and_ask_bike_count)
                ],
                self.BIKE_COUNT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_date)
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
                                   self.check_admin_and_ask_bikes_num)
                ],
                self.BIKES_NUM: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_foreign_phone)
                ],
                self.FOREIGN_PHONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_admin_date)
                ],
                self.FOREIGN_DATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_admin_start)
                ],
                self.FOREIGN_START: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_admin_end)
                ],
                self.FOREIGN_END: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.make_foreign_book)
                ]
            },
            fallbacks=[]
        )

        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(create_conv_handler)
        application.add_handler(booking_conv_handler)
        application.add_handler(admin_conv_handler)

        application.run_polling()
