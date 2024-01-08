import datetime
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.conf import settings

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (ContextTypes, ApplicationBuilder,
                          CommandHandler, MessageHandler, filters,
                          ConversationHandler)

from btr.bookings.bot_handlers import generate_verification_code, \
    check_verification_code, get_free_slots_for_bot_view, \
    check_available_start_time, check_available_hours, check_admin_password, \
    extract_start_times, extract_hours
from btr.bookings.db_handlers import (create_user_by_bot_as,
                                      create_booking_by_bot_as,
                                      check_user_exist_as,
                                      check_available_field_as,
                                      reset_user_password_as,
                                      check_booking_status_as,
                                      change_booking_status_as, SlotsFinder,
                                      create_booking_by_admin_as,
                                      )
from btr.bookings.tasks import send_details
from btr.bookings.bot_validators import validate_bike_quantity, \
    validate_phone_number, validate_date, validate_time, validate_time_range, \
    validate_email, validate_hours, validate_first_name
from btr.users.tasks import (send_data_from_tg,
                             send_verification_code_from_tg,
                             send_recover_message_from_tg)
from .bot_exceptions import BusyDayException, TimeIsNotAvailable, \
    InvalidTimeFormat, InvalidDateFormat, WrongBikeCount, InvalidEmailFormat, \
    DateInPastException, SameStatusSelected, WrongAdminPassword


class BookingBot:
    ADMIN = range(1)
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def __init__(self, token: str):
        self.token = token

    def run(self):
        application = ApplicationBuilder().token(self.token).build()

        start_command = CommandHandler(
            'start', StartCommandHandler().handle
        )
        help_command = CommandHandler(
            'help', HelpCommandHandler().handle
        )
        unknown_command_handler = MessageHandler(
            filters.COMMAND,
            UnknownCommandHandler().handle
        )
        password_reset_conversation = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'reset', ResetPasswordConversation().ask_email
                )
            ],
            states={
                ResetPasswordConversation.RESET_EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ResetPasswordConversation().ask_verification_code,
                    )
                ],
                ResetPasswordConversation.VERIFICATION_CODE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        ResetPasswordConversation().send_reset_password,
                    )
                ],
            },
            fallbacks=[]
        )
        create_account_conversation = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'create',
                    CreateAccountConversation().ask_username,
                )
            ],
            states={
                CreateAccountConversation.USERNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        CreateAccountConversation().ask_first_name,
                    )
                ],
                CreateAccountConversation.FIRST_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        CreateAccountConversation().ask_email,
                    )
                ],
                CreateAccountConversation.EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        CreateAccountConversation().ask_phone_number,
                    )
                ],
                CreateAccountConversation.PHONE_NUMBER: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        CreateAccountConversation().create_account,
                    )
                ]
            },
            fallbacks=[]
        )
        booking_conversation = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'book',
                    BookingConversation().ask_email,
                )
            ],
            states={
                BookingConversation.EMAIL_CHECK: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BookingConversation().ask_bike_count,
                    )
                ],
                BookingConversation.BIKE_COUNT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BookingConversation().ask_date,
                    )
                ],
                BookingConversation.BOOK_DATE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BookingConversation().ask_start_time,
                    )
                ],
                BookingConversation.BOOK_START_TIME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BookingConversation().ask_hours,
                    )
                ],
                BookingConversation.BOOK_HOURS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BookingConversation().make_booking,
                    )
                ]
            },
            fallbacks=[]
        )
        admin_conversation = ConversationHandler(
            entry_points=[
                CommandHandler(
                    'admin',
                    AdminAccessConversation().ask_password,
                )
            ],
            states={
                AdminAccessConversation.PASSWORD: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        AdminAccessConversation().check_admin_password,
                    )
                ]
            },
            fallbacks=[]
        )
        # change_status_conversation = ConversationHandler(
        #     entry_points=[
        #         CommandHandler(
        #             'change',
        #             BookingChangeStatusConversation().ask_id,
        #         )
        #     ],
        #     states={
        #         BookingChangeStatusConversation.BOOKING_ID: [
        #             MessageHandler(
        #                 filters.TEXT & ~filters.COMMAND,
        #                 BookingChangeStatusConversation().ask_status,
        #             )
        #         ],
        #         BookingChangeStatusConversation.BOOKING_STATUS: [
        #             MessageHandler(
        #                 filters.TEXT & ~filters.COMMAND,
        #                 BookingChangeStatusConversation().change_status,
        #             )
        #         ]
        #     },
        #     fallbacks=[]
        # )

        application.add_handler(start_command)
        application.add_handler(help_command)
        application.add_handler(password_reset_conversation)
        application.add_handler(create_account_conversation)
        application.add_handler(booking_conversation)

        application.add_handler(admin_conversation)

        # application.add_handler(unknown_command_handler)
        application.run_polling()


class StartCommandHandler:
    @staticmethod
    async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Hi! 16+\nI am BroTeamRacing booking bot\n'
            'There are commands that you can type:\n'
            'To create an account (required for booking): /create\n'
            'To reset your forgotten password: /reset\n'
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


class HelpCommandHandler:
    @staticmethod
    async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'If you have any questions or problems with your booking,'
            '\nPlease contact me at:\n'
            '+7 999 235-00-91\n'
            'Or\nhttps://vk.me/broteamracing'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )


class UnknownCommandHandler:
    @staticmethod
    async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
        command = update.message.text
        message = _(
            'Unknown command: {command} !\n'
            'You can see available commands below:\n'
            '/start - to see main page\n'
            '/help - to see help message\n'
            '/create - to create an account\n'
            '/book - to book ride (required account)\n'
            '/reset - to reset your forgotten password'
        ).format(command=command)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )


class ResetPasswordConversation:
    RESET_EMAIL, VERIFICATION_CODE = range(2)

    async def ask_email(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        message = _(
            'Enter a valid email to which a confirmation code will be sent:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        return self.RESET_EMAIL

    async def ask_verification_code(self, update: Update, context):
        email = update.message.text
        message = ''
        try:
            await check_user_exist_as(email)
            context.user_data['reset_email'] = email
            message = _(
                'Verification code was sent by {email} !\n'
                'Write the six-digit code from the email:'
            ).format(email=email)
            code = generate_verification_code()
            context.user_data['ver_code'] = code
            send_verification_code_from_tg.delay(email, code)
            return self.VERIFICATION_CODE
        except NameError:
            message = _(
                'User with email {email} does not exist!\n'
                'Try spell email again (case sensitive)\n'
                'Or create a new account: /create'
            ).format(email=email)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    @staticmethod
    async def send_reset_password(update: Update, context):
        code = update.message.text
        source_code = context.user_data.get('ver_code')
        user_email = context.user_data.get('reset_email')
        message = ''
        try:
            check_verification_code(source_code, code)
            password = await reset_user_password_as(user_email)
            send_recover_message_from_tg.delay(user_email, password)
            message = _(
                'Password was reset successfully!\n'
                'A new sign in info was sent to your email:\n'
                '{email}'
            ).format(email=user_email)
            return ConversationHandler.END
        except ValueError:
            message = _(
                'Verification codes does not match!\n'
                'Try spell verification code again:'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )


class CreateAccountConversation:
    USERNAME, FIRST_NAME, EMAIL, PHONE_NUMBER = range(4)

    async def ask_username(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Let\'s create an account!\n'
            'Please, provide a Username\n'
            '*max length 40 symbols:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.USERNAME

    async def ask_first_name(self, update: Update, context):
        username = update.message.text
        is_username_available = await check_available_field_as(username)
        message = ''
        if is_username_available:
            try:
                validate_first_name(username)
                context.user_data['username'] = username
                message = _(
                    'Great {username}!\n'
                    'Now, please provide your first name:'
                ).format(username=username)
                return self.FIRST_NAME
            except ValueError:
                message = _(
                    'Username can\'t be greater than 40 symbols!\n'
                    'Try again!'
                )
            finally:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
        else:
            message = _(
                'User with Username: {username} already exists!\n'
                'Try another one!:'
            ).format(username=username)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    async def ask_email(self, update: Update, context):
        first_name = update.message.text
        message = ''
        try:
            validate_first_name(first_name)
            context.user_data['first_name'] = first_name
            message = _(
                'Super, {name}!\n'
                'Now i need your valid Email:'
            ).format(name=first_name)
            return self.EMAIL
        except ValueError:
            message = _(
                'The first name length greater than 40 symbols!\n'
                'Max length are 40 symbols!\n'
                'Try again!'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    async def ask_phone_number(self, update: Update, context):
        email = update.message.text
        message = ''
        is_email_available = await check_available_field_as(email)
        if is_email_available:
            try:
                validate_email(email)
                context.user_data['email'] = email
                message = _(
                    'We are almost finished, all that remains is to enter '
                    'the phone number:\n'
                    'Phone number must be in format: +71234567890:'
                )
                return self.PHONE_NUMBER
            except ValueError:
                message = _(
                    'Invalid email format: {email}!\n'
                    'Check your spelling and try again!'
                ).format(email=email)
            finally:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
        else:
            message = _(
                'User with email: {email} already exists!\n'
                'If you have lost access to your account,\n'
                'you can reset your password by command: /reset\n'
                'Or type email again:'
            ).format(email=email)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    @staticmethod
    async def create_account(update: Update, context):
        phone_number = update.message.text
        message = ''
        is_phone_available = await check_available_field_as(phone_number)
        if is_phone_available:
            try:
                context.user_data['phone_number'] = phone_number
                user_data = context.user_data
                password = await create_user_by_bot_as(user_data)
                send_data_from_tg.delay(
                    user_data.get('email'),
                    user_data.get('first_name'),
                    user_data.get('username'),
                    user_data.get('phone_number'),
                    password,
                )
                message = _(
                    'User created successfully!\n'
                    'An email with your login information will be sent to '
                    '{email}'
                    '\nYou can check your bookings status in your profile on\n'
                    'broteamracing.ru'
                ).format(email=user_data.get('email'))
                return ConversationHandler.END
            #  String for dev env, remove before deployment!!!
            except Exception as e:
                message = str(e)
            finally:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
        else:
            message = _(
                'User with phone number: {phone} already exists!\n'
                'If you have lost access to your account,\n'
                'you can reset your password by command: /reset\n'
                'Or type phone number again:'
            ).format(phone=phone_number)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )


class BookingConversation:
    EMAIL_CHECK, BIKE_COUNT, BOOK_DATE, BOOK_START_TIME, BOOK_HOURS = range(5)

    async def ask_email(self, update: Update,
                        context: ContextTypes.DEFAULT_TYPE):
        message = _('Please enter your email to proceed with booking:')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.EMAIL_CHECK

    async def ask_bike_count(self, update: Update, context):
        email = update.message.text
        message = ''
        try:
            validate_email(email)
            await check_user_exist_as(email)
            context.user_data['user_email'] = email
            message = _(
                'User with email {email} find successfully!\n'
                'Please tell me, how many bikes you want to rent?\n'
                'Min: 1, Max: 4'
            ).format(email=email)
            return self.BIKE_COUNT
        except InvalidEmailFormat:
            message = _(
                'Invalid email format: {email}!\n'
                'Check your spelling and try again:'
            ).format(email=email)
        except ObjectDoesNotExist:
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
                'Ok! You are served {bike_count} bikes in this ride.\n'
                'Now please tell me the date you would like to make'
                ' a reservation for\n'
                'in format YYYY-MM-DD:'
            ).format(bike_count=bike_count)
            return self.BOOK_DATE
        except WrongBikeCount:
            message = _(
                'Invalid bikes rental count: {bike_count}!\n'
                'Bikes count must be at 1-4!\n'
                'Try again:'
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
            available_slots = await get_free_slots_for_bot_view(date)
            context.user_data['book_date'] = date
            message = _(
                'Ok!\n'
                'What time should you rent?\n'
                'Available time slots:\n\n{slots}\n\n'
                'Please, type in format: HH:MM'
            ).format(slots=available_slots)
            return self.BOOK_START_TIME
        except InvalidDateFormat:
            message = _(
                'Invalid date format: {date}!\n'
                'Date format must be: YYYY-MM-DD (with "-")\n'
                'Try again:'
            ).format(date=date)
        except DateInPastException:
            message = _(
                'Rent day cannot be in past!\n'
                'Today is {today}\n'
                'Try again:'
            ).format(today=datetime.datetime.now().date())
        except BusyDayException:
            message = _(
                'On {date} no available slots! :(\n'
                'Pick up another date:\n'
            ).format(date=date)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )

    async def ask_hours(self, update: Update, context):
        start = update.message.text
        date = context.user_data.get('book_date')
        available_slots = await get_free_slots_for_bot_view(date)
        message = ''
        try:
            validate_time(start)
            check_available_start_time(start, available_slots)
            context.user_data['book_start_time'] = start
            message = _(
                'You will be scheduled for rental on {date}\n'
                'How long do you plan to ride?\n'
                'Available slots:\n\n'
                '{slots}\n\n'
                'Your start time:\n\n{time}\n\n'
                'Enter the number of hours (example: 2):'
            ).format(date=date, slots=available_slots, time=start)
            return self.BOOK_HOURS
        except TimeIsNotAvailable:
            message = _(
                'The time {start} is already booked!\n'
                'Please select a start time based on available slots:\n\n'
                '{slots}\n\n'
            ).format(start=start, slots=available_slots)
        except InvalidTimeFormat:
            message = _(
                'Invalid time format: {start}!\n'
                'Correct format is: HH:MM\n'
                'Try again!'
            ).format(start=start)
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
        start_time = book_data.get('book_start_time')
        date = book_data.get('book_date')
        available_slots = await get_free_slots_for_bot_view(date)
        message = ''
        try:
            validate_hours(hours)
            check_available_hours(start_time, hours, available_slots)
            email = book_data.get('user_email')
            interval = await create_booking_by_bot_as(book_data)
            date = book_data.get('book_date')
            start = interval.get('start_time')
            end = interval.get('end_time')
            bike_count = book_data.get('bike_count')
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
            return ConversationHandler.END
        except TimeIsNotAvailable:
            message = _(
                '{hours} hours exceeds the available booking slot\n'
                'Available slots is:\n\n{slots}\n\n'
                'Your start time is:\n\n{time}\n\n'
                'Please, type allowable count of hours again:'
            ).format(hours=hours, slots=available_slots, time=start_time)
        except NameError:
            message = _(
                'Can\'t find phone number to user {email}!\n'
            ).format(email=context.user_data.get('user_email'))
        except ValueError:
            message = _(
                'Invalid hours rate: {hours}!\n'
                'Type format: 1-24\n'
                'Try again!'
            ).format(hours=hours)
        # DEV string, remove before deployment!!!
        except Exception as e:
            message = str(e)
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )


class ForeignBookingConversation:
    PASSWORD, BIKES, PHONE, DATE, START, HOURS = range(6)

    async def ask_password(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'To make a foreign book, type admin password:'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        return self.PASSWORD

    async def ask_bikes(self, update, context):
        password = update.message.text
        options = ['1', '2', '3', '4']
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(option)] for option in options],
            resize_keyboard=True
        )
        try:
            check_admin_password(password)
            message = _(
                'Admin privileges confirmed!\n'
                'How many bikes should i rent?\n'
                'Min: 1, Max: 4'
            )
            await update.message.reply_text(message, reply_markup=keyboard)
            return self.BIKES
        except WrongAdminPassword:
            message = _(
                'Wrong password, try again!\n'
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_phone(self, update, context):
        bikes_num = update.message.text
        message = ''
        try:
            validate_bike_quantity(bikes_num)
            context.user_data['bikes_num'] = update.message.text
            message = _(
                'Ok!\n'
                'Type rider phone number (for example: +71234567890):'
            )
            return self.PHONE
        except WrongBikeCount:
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

    async def ask_date(self, update, context):
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
            return self.DATE
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

    async def ask_start(self, update, context):
        foreign_date = update.message.text
        slots = SlotsFinder(foreign_date)
        available_slots: list = await slots.find_available_slots_as()
        available_starts = extract_start_times(available_slots)
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(option)] for option in available_starts],
            resize_keyboard=True
        )
        try:
            validate_date(foreign_date)
            context.user_data['book_date'] = foreign_date
            message = _(
                'Ok!\n'
                'Now enter the time of start in format HH:MM:'
            )
            await update.message.reply_text(message, reply_markup=keyboard)
            return self.START
        except ValueError:
            message = _(
                'Invalid date format: {date}!\n'
                'Date format must be: YYYY-MM-DD (with "-")\n'
                'Try again!'
            ).format(date=foreign_date)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_hours(self, update: Update, context):
        start = update.message.text
        date = context.user_data.get('book_date')
        slots = SlotsFinder(date)
        available_slots = await slots.find_available_slots_as()
        options = extract_hours(available_slots, start)
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(option)] for option in options],
            resize_keyboard=True
        )
        message = ''
        try:
            validate_time(start)
            # check_available_start_time(start, available_slots)
            context.user_data['book_start_time'] = start
            message = _(
                'You will be scheduled for rental on {date}\n'
                'How long do you plan to ride?\n'
                'Available slots:\n\n'
                '{slots}\n\n'
                'Your start time:\n\n{time}\n\n'
                'Enter the number of hours (example: 2):'
            ).format(date=date, slots=available_slots, time=start)
            await update.message.reply_text(message, reply_markup=keyboard)
            return self.HOURS
        except TimeIsNotAvailable:
            message = _(
                'The time {start} is already booked!\n'
                'Please select a start time based on available slots:\n\n'
                '{slots}\n\n'
            ).format(start=start, slots=available_slots)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
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


class AdminChangeStatusConversation:
    PASSWORD, BOOKING_ID, BOOKING_STATUS = range(3)

    async def ask_password(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        message = _(
            'Hi, admin!\n'
            'Confirm admin rights, type a password:\n'
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        return self.PASSWORD

    async def ask_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        password = update.message.text
        message = ''
        try:
            check_admin_password(password)
            message = _(
                'Admin privileges confirmed!\n'
                'Please, type booking ID:\n'
            )
            return self.BOOKING_ID
        except WrongAdminPassword:
            message = _(
                'Wrong password, try again!\n'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    async def ask_status(self, update, context):
        booking_id = update.message.text
        statuses = [_('confirmed'), _('canceled')]
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(status)] for status in statuses],
            resize_keyboard=True
        )
        try:
            booking_info = await check_booking_status_as(booking_id)
            context.user_data['booking_id'] = booking_id
            message = _(
                'The booking status with id {id}: {status}\n'
                'Booking date: {date}, {start} - {end}\n'
                'To change status, choose one of them below'
            ).format(
                id=booking_id,
                status=booking_info.get('status'),
                date=booking_info.get('date'),
                start=booking_info.get('start'),
                end=booking_info.get('end'),
            )
            await update.message.reply_text(message, reply_markup=keyboard)
            return self.BOOKING_STATUS
        except ObjectDoesNotExist:
            message = _(
                'Booking with id {id} does not exist!\n'
                'Check your spelling and try again:'
            ).format(id=booking_id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

    @staticmethod
    async def change_status(update, context):
        status = update.message.text
        message = ''
        try:
            booking_id = context.user_data.get('booking_id')
            old_status = await change_booking_status_as(booking_id, status)
            message = _(
                'Booking status #{id} changed successfully!\n'
                'From: {old}\n'
                'To: {new}'
            ).format(id=booking_id, old=old_status, new=status)
            return ConversationHandler.END
        except SameStatusSelected:
            message = _(
                'You can\'t choose the same status!\n'
                'Choose another one'
            )
        finally:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
            )

# class BookingBot:
#
#     logging.basicConfig(
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         level=logging.INFO
#     )
#     USERNAME, FIRST_NAME, EMAIL, PHONE_NUMBER = range(4)
#     EMAIL_CHECK, BIKE_COUNT, BOOK_DATE, BOOK_START_TIME, BOOK_HOURS = range(5)
#     (ADMIN_CHECK, BIKES_NUM, FOREIGN_PHONE,
#      FOREIGN_DATE, FOREIGN_START, FOREIGN_END) = range(6)
#     RESET_EMAIL, VERIFICATION_CODE = range(2)
#
#     def __init__(self, token: str):
#         self.token = token
#
    # @staticmethod
    # async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     # message = _(
    #     #     'Hi! 16+\nI am BroTeamRacing booking bot\n'
    #     #     'There are commands that you can type:\n'
    #     #     'To create an account (required for booking): /create\n'
    #     #     'To reset your forgotten password: /reset\n'
    #     #     'To book ride right now: /book\n'
    #     #     'To see help message: /help\n'
    #     #     'By details you can visit our web-site:\n'
    #     #     'broteamracing.ru\n'
    #     #     'or vk-group:\n'
    #     #     'vk.com/broteamracing'
    #     # )
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text=message
    #     )
#
#     @staticmethod
#     async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#         help_text = _(
#             'If you have any questions or problems with your booking,'
#             '\nPlease contact me at:\n'
#             '+7 999 235-00-91\n'
#             'Or\nhttps://vk.me/broteamracing'
#         )
#         await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=help_text
#         )
#
#     @staticmethod
#     async def unknown_command(update: Update,
#                               context: ContextTypes.DEFAULT_TYPE):
#         command = update.message.text
#         message = _(
#             'Unknown command: {command} !\n'
#             'You can see available commands below:\n'
#             '/start - to see main page\n'
#             '/help - to see help message\n'
#             '/create - to create an account\n'
#             '/book - to book ride (required account)\n'
#             '/reset - to reset your forgotten password'
#         ).format(command=command)
#         await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=message
#         )
#
    # async def reset_command_and_ask_email(
    #         self, update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     message = _(
    #         'Enter a valid email to which a confirmation code will be sent:'
    #     )
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text=message
    #     )
    #     return self.RESET_EMAIL
    #
    # async def ask_verification_code(self, update: Update, context):
    #     email = update.message.text
    #     message = ''
    #     try:
    #         await check_user_exist_as(email)
    #         context.user_data['reset_email'] = email
    #         message = _(
    #             'Verification code was sent by {email} !\n'
    #             'Write the six-digit code from the email:'
    #         ).format(email=email)
    #         code = generate_verification_code()
    #         context.user_data['ver_code'] = code
    #         send_verification_code_from_tg.delay(email, code)
    #         return self.VERIFICATION_CODE
    #     except NameError:
    #         message = _(
    #             'User with email {email} does not exist!\n'
    #             'Try spell email again (case sensitive)\n'
    #             'Or create a new account: /create'
    #         ).format(email=email)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # @staticmethod
    # async def send_reset_password(update: Update, context):
    #     code = update.message.text
    #     source_code = context.user_data.get('ver_code')
    #     user_email = context.user_data.get('reset_email')
    #     message = ''
    #     try:
    #         check_verification_code(source_code, code)
    #         password = await reset_user_password_as(user_email)
    #         send_recover_message_from_tg.delay(user_email, password)
    #         message = _(
    #             'Password was reset successfully!\n'
    #             'A new sign in info was sent to your email:\n'
    #             '{email}'
    #         ).format(email=user_email)
    #         return ConversationHandler.END
    #     except ValueError:
    #         message = _(
    #             'Verification codes does not match!\n'
    #             'Try spell verification code again:'
    #         )
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
#
    # async def create_command_and_ask_username(
    #         self, update: Update, context: ContextTypes.DEFAULT_TYPE
    # ):
    #     message = _(
    #         'Let\'s create an account!\n'
    #         'Please, provide a Username\n'
    #         '*max length 40 symbols:'
    #     )
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text=message
    #     )
    #     return self.USERNAME
    #
    # async def ask_first_name(self, update: Update, context):
    #     username = update.message.text
    #     is_username_available = await check_available_field_as(username)
    #     message = ''
    #     if is_username_available:
    #         try:
    #             validate_first_name(username)
    #             context.user_data['username'] = username
    #             message = _(
    #                 'Great {username}!\n'
    #                 'Now, please provide your first name:'
    #             ).format(username=username)
    #             return self.FIRST_NAME
    #         except ValueError:
    #             message = _(
    #                 'Username can\'t be greater than 40 symbols!\n'
    #                 'Try again!'
    #             )
    #         finally:
    #             await context.bot.send_message(
    #                 chat_id=update.effective_chat.id,
    #                 text=message
    #             )
    #     else:
    #         message = _(
    #             'User with Username: {username} already exists!\n'
    #             'Try another one!:'
    #         ).format(username=username)
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # async def ask_email(self, update: Update, context):
    #     first_name = update.message.text
    #     message = ''
    #     try:
    #         validate_first_name(first_name)
    #         context.user_data['first_name'] = first_name
    #         message = _(
    #             'Super, {name}!\n'
    #             'Now i need your valid Email:'
    #         ).format(name=first_name)
    #         return self.EMAIL
    #     except ValueError:
    #         message = _(
    #             'The first name length greater than 40 symbols!\n'
    #             'Max length are 40 symbols!\n'
    #             'Try again!'
    #         )
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # async def ask_phone_number(self, update: Update, context):
    #     email = update.message.text
    #     message = ''
    #     is_email_available = await check_available_field_as(email)
    #     if is_email_available:
    #         try:
    #             validate_email(email)
    #             context.user_data['email'] = email
    #             message = _(
    #                 'We are almost finished, all that remains is to enter '
    #                 'the phone number:\n'
    #                 'Phone number must be in format: +71234567890:'
    #             )
    #             return self.PHONE_NUMBER
    #         except ValueError:
    #             message = _(
    #                 'Invalid email format: {email}!\n'
    #                 'Check your spelling and try again!'
    #             ).format(email=email)
    #         finally:
    #             await context.bot.send_message(
    #                 chat_id=update.effective_chat.id,
    #                 text=message
    #             )
    #     else:
    #         message = _(
    #             'User with email: {email} already exists!\n'
    #             'If you have lost access to your account,\n'
    #             'you can reset your password by command: /reset\n'
    #             'Or type email again:'
    #         ).format(email=email)
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # @staticmethod
    # async def create_account(update: Update, context):
    #     phone_number = update.message.text
    #     message = ''
    #     is_phone_available = await check_available_field_as(phone_number)
    #     if is_phone_available:
    #         try:
    #             context.user_data['phone_number'] = phone_number
    #             user_data = context.user_data
    #             password = await create_user_by_bot_as(user_data)
    #             send_data_from_tg.delay(
    #                 user_data.get('email'),
    #                 user_data.get('first_name'),
    #                 user_data.get('username'),
    #                 user_data.get('phone_number'),
    #                 password,
    #             )
    #             message = _(
    #                 'User created successfully!\n'
    #                 'An email with your login information will be sent to '
    #                 '{email}'
    #                 '\nYou can check your bookings status in your profile on\n'
    #                 'broteamracing.ru'
    #             ).format(email=user_data.get('email'))
    #             return ConversationHandler.END
    #         #  String for dev env, remove before deployment!!!
    #         except Exception as e:
    #             message = str(e)
    #         finally:
    #             await context.bot.send_message(
    #                 chat_id=update.effective_chat.id,
    #                 text=message
    #             )
    #     else:
    #         message = _(
    #             'User with phone number: {phone} already exists!\n'
    #             'If you have lost access to your account,\n'
    #             'you can reset your password by command: /reset\n'
    #             'Or type phone number again:'
    #         ).format(phone=phone_number)
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
#
    # async def book_command(self, update: Update,
    #                        context: ContextTypes.DEFAULT_TYPE):
    #     message = _(
    #         'Please enter your email to proceed with booking:'
    #     )
    #
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text=message
    #     )
    #     return self.EMAIL_CHECK
    #
    # async def check_user_and_ask_bike_count(self, update: Update, context):
    #     email = update.message.text
    #     message = ''
    #     try:
    #         validate_email(email)
    #         await check_user_exist_as(email)
    #         context.user_data['user_email'] = email
    #         message = _(
    #             'User with email {email} find successfully!\n'
    #             'Please tell me, how many bikes you want to rent?\n'
    #             'Min: 1, Max: 4'
    #         ).format(email=email)
    #         return self.BIKE_COUNT
    #     except InvalidEmailFormat:
    #         message = _(
    #             'Invalid email format: {email}!\n'
    #             'Check your spelling and try again:'
    #         ).format(email=email)
    #     except ObjectDoesNotExist:
    #         message = _(
    #             'Can\'t find user with email {email} :(\n'
    #             'Check your spelling or create a new account: /create\n'
    #             'Type a help command: /help\n'
    #             'Or try again:'
    #         ).format(email=email)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_date(self, update: Update, context):
    #     bike_count = update.message.text
    #     message = ''
    #     try:
    #         validate_bike_quantity(bike_count)
    #         context.user_data['bike_count'] = bike_count
    #         message = _(
    #             'Ok! You are served {bike_count} bikes in this ride.'
    #             'Now please tell me the date you would like to make'
    #             ' a reservation for\n'
    #             'in format YYYY-MM-DD:'
    #         ).format(bike_count=bike_count)
    #         return self.BOOK_DATE
    #     except WrongBikeCount:
    #         message = _(
    #             'Invalid bikes rental count: {bike_count}!\n'
    #             'Bikes count must be at 1-4!\n'
    #             'Try again:'
    #         ).format(bike_count=bike_count)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_start_time(self, update: Update, context):
    #     date = update.message.text
    #     message = ''
    #     try:
    #         validate_date(date)
    #         available_slots = await get_free_slots_for_bot_view(date)
    #         context.user_data['book_date'] = date
    #         message = _(
    #             'Ok!\n'
    #             'What time should you rent?\n'
    #             'Available time slots:\n\n{slots}\n\n'
    #             'Please, type in format: HH:MM'
    #         ).format(slots=available_slots)
    #         return self.BOOK_START_TIME
    #     except InvalidDateFormat:
    #         message = _(
    #             'Invalid date format: {date}!\n'
    #             'Date format must be: YYYY-MM-DD (with "-")\n'
    #             'Try again:'
    #         ).format(date=date)
    #     except DateInPastException:
    #         message = _(
    #             'Rent day cannot be in past!\n'
    #             'Today is {today}\n'
    #             'Try again:'
    #         ).format(today=datetime.datetime.now().date())
    #     except BusyDayException:
    #         message = _(
    #             'On {date} no available slots! :(\n'
    #             'Pick up another date:\n'
    #         ).format(date=date)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # async def ask_hours(self, update: Update, context):
    #     start = update.message.text
    #     date = context.user_data.get('book_date')
    #     available_slots = await get_free_slots_for_bot_view(date)
    #     message = ''
    #     try:
    #         validate_time(start)
    #         check_available_start_time(start, available_slots)
    #         context.user_data['book_start_time'] = start
    #         message = _(
    #             'You will be scheduled for rental on {date}\n'
    #             'How long do you plan to ride?\n'
    #             'Available slots:\n\n'
    #             '{slots}\n\n'
    #             'Your start time:\n\n{time}\n\n'
    #             'Enter the number of hours (example: 2):'
    #         ).format(date=date, slots=available_slots, time=start)
    #         return self.BOOK_HOURS
    #     except TimeIsNotAvailable:
    #         message = _(
    #             'The time {start} is already booked!\n'
    #             'Please select a start time based on available slots:\n\n'
    #             '{slots}\n\n'
    #         ).format(start=start, slots=available_slots)
    #     except InvalidTimeFormat:
    #         message = _(
    #             'Invalid time format: {start}!\n'
    #             'Correct format is: HH:MM\n'
    #             'Try again!'
    #         ).format(start=start)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
    #
    # @staticmethod
    # async def make_booking(update: Update, context):
    #     hours = update.message.text
    #     context.user_data['book_hours'] = hours
    #     book_data = context.user_data
    #     start_time = book_data.get('book_start_time')
    #     date = book_data.get('book_date')
    #     available_slots = await get_free_slots_for_bot_view(date)
    #     message = ''
    #     try:
    #         validate_hours(hours)
    #         check_available_hours(start_time, hours, available_slots)
    #         email = book_data.get('user_email')
    #         interval = await create_booking_by_bot_as(book_data)
    #         date = book_data.get('book_date')
    #         start = interval.get('start_time')
    #         end = interval.get('end_time')
    #         bike_count = book_data.get('bike_count')
    #         message = _(
    #             'Booking created successfully!\n'
    #             'Details:\n'
    #             'Date of ride: {date}\n'
    #             'Time of ride: from {start} to {end}\n'
    #             'Number of bikes in the booking: {bike_count}\n'
    #             'We have sent you complete booking information by email:\n'
    #             '{email}'
    #         ).format(date=date, start=start, end=end,
    #                  bike_count=bike_count, email=email)
    #         send_details.delay(email, date, start, end, bike_count)
    #         return ConversationHandler.END
    #     except TimeIsNotAvailable:
    #         message = _(
    #             '{hours} hours exceeds the available booking slot\n'
    #             'Available slots is:\n\n{slots}\n\n'
    #             'Your start time is:\n\n{time}\n\n'
    #             'Please, type allowable count of hours again:'
    #         ).format(hours=hours, slots=available_slots, time=start_time)
    #     except NameError:
    #         message = _(
    #             'Can\'t find phone number to user {email}!\n'
    #         ).format(email=context.user_data.get('user_email'))
    #     except ValueError:
    #         message = _(
    #             'Invalid hours rate: {hours}!\n'
    #             'Type format: 1-24\n'
    #             'Try again!'
    #         ).format(hours=hours)
    #     # DEV string, remove before deployment!!!
    #     except Exception as e:
    #         message = str(e)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message
    #         )
#
    # async def admin_command(self, update: Update,
    #                         context: ContextTypes.DEFAULT_TYPE):
    #     message = _(
    #         'Hi, admin!\n'
    #         'Confirm admin rights, type a password:\n'
    #     )
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text=message
    #     )
    #     return self.ADMIN_CHECK
    #
    # async def check_admin_and_ask_bikes_num(self, update: Update, context):
    #     password = update.message.text
    #     if password == settings.TG_ADMIN_PASSWORD:
    #         message = _(
    #             'Admin privileges confirmed!\n'
    #             'How many bikes should i rent?\n'
    #             'Min: 1, Max: 4'
    #         )
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #         return self.BIKES_NUM
    #     else:
    #         message = _(
    #             'Wrong password, try again!\n'
    #             '/admin'
    #         )
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_foreign_phone(self, update: Update, context):
    #     bikes_num = update.message.text
    #     message = ''
    #     try:
    #         validate_bike_quantity(bikes_num)
    #         context.user_data['bikes_num'] = update.message.text
    #         message = _(
    #             'Ok!\n'
    #             'Type rider phone number (for example: +71234567890):'
    #         )
    #         return self.FOREIGN_PHONE
    #     except ValueError:
    #         message = _(
    #             'Bike count {bikes_num} is invalid!\n'
    #             'The valid counter is at 1-4!\n'
    #             'Try again'
    #         ).format(bikes_num=bikes_num)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_admin_date(self, update: Update, context):
    #     foreign_phone = update.message.text
    #     message = ''
    #     try:
    #         validate_phone_number(foreign_phone)
    #         context.user_data['foreign_phone'] = foreign_phone
    #         message = _(
    #             'Got it!\n'
    #             'Type a date for client: {phone}\n'
    #             'In format YYYY-MM-DD:'
    #         ).format(phone=context.user_data.get('foreign_phone'))
    #         return self.FOREIGN_DATE
    #     except ValueError:
    #         message = _(
    #             'Invalid phone number: {phone}!\n'
    #             'Phone number format must be: +71234567890\n'
    #             'Try again!'
    #         ).format(phone=foreign_phone)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_admin_start(self, update: Update, context):
    #     foreign_date = update.message.text
    #     message = ''
    #     try:
    #         validate_date(foreign_date)
    #         context.user_data['foreign_date'] = foreign_date
    #         message = _(
    #             'Ok!\n'
    #             'Now enter the time of start in format HH:MM:'
    #         )
    #         return self.FOREIGN_START
    #     except ValueError:
    #         message = _(
    #             'Invalid date format: {date}!\n'
    #             'Date format must be: YYYY-MM-DD (with "-")\n'
    #             'Try again!'
    #         ).format(date=foreign_date)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # async def ask_admin_end(self, update: Update, context):
    #     start = update.message.text
    #     message = ''
    #     try:
    #         validate_time(start)
    #         context.user_data['foreign_start'] = start
    #         message = _(
    #             'Ok!\n'
    #             'Now enter the time of end in format HH:MM:'
    #         )
    #         return self.FOREIGN_END
    #     except ValueError:
    #         message = _(
    #             'Invalid time format: {start}!\n'
    #             'Time format must be: HH:MM (with ":")\n'
    #             'Try again!'
    #         ).format(start=start)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
    #
    # @staticmethod
    # async def make_foreign_book(update: Update, context):
    #     start = context.user_data.get('foreign_start')
    #     end = update.message.text
    #     message = ''
    #     try:
    #         validate_time(end)
    #         validate_time_range(start, end)
    #         context.user_data['foreign_end'] = end
    #         book_data = context.user_data
    #         await create_booking_by_admin_as(book_data)
    #         message = _(
    #             'Booking created successfully!\n'
    #             'Details:\n'
    #             'Bikes rented: {bikes_num}\n'
    #             'Client\'s phone: {phone}\n'
    #             'Date: {date}\n'
    #             'From {start} to {end}'
    #         ).format(
    #             bikes_num=book_data.get('bikes_num'),
    #             phone=book_data.get('foreign_phone'),
    #             date=book_data.get('foreign_date'),
    #             start=book_data.get('foreign_start'),
    #             end=book_data.get('foreign_end'),
    #         )
    #         return ConversationHandler.END
    #     except ValueError:
    #         message = _(
    #             'End time must be greater than Start time!\n'
    #             'Your Start: {start}\n'
    #             'Your End: {end}\n'
    #             'Try again!'
    #         ).format(start=start, end=end)
    #     except Exception as e:
    #         message = str(e)
    #     finally:
    #         await context.bot.send_message(
    #             chat_id=update.effective_chat.id,
    #             text=message,
    #         )
#
#     def run(self):
#         application = ApplicationBuilder().token(self.token).build()
#
#         start_handler = CommandHandler('start', self.start)
#         help_handler = CommandHandler('help', self.help_command)
#         unknown_command_handler = MessageHandler(
#             filters.COMMAND,
#             self.unknown_command
#         )
#         create_conv_handler = ConversationHandler(
#             entry_points=[
#                 CommandHandler(
#                     'create', self.create_command_and_ask_username
#                 )
#             ],
#             states={
#                 self.USERNAME: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_first_name)
#                 ],
#                 self.FIRST_NAME: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_email)
#                 ],
#                 self.EMAIL: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_phone_number)
#                 ],
#                 self.PHONE_NUMBER: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.create_account)]
#             },
#             fallbacks=[]
#         )
#
        # booking_conv_handler = ConversationHandler(
        #     entry_points=[
        #         CommandHandler('book', self.book_command)
        #     ],
        #     states={
        #         self.EMAIL_CHECK: [
        #             MessageHandler(filters.TEXT & ~filters.COMMAND,
        #                            self.check_user_and_ask_bike_count)
        #         ],
        #         self.BIKE_COUNT: [
        #             MessageHandler(filters.TEXT & ~filters.COMMAND,
        #                            self.ask_date)
        #         ],
        #         self.BOOK_DATE: [
        #             MessageHandler(filters.TEXT & ~filters.COMMAND,
        #                            self.ask_start_time)
        #         ],
        #         self.BOOK_START_TIME: [
        #             MessageHandler(filters.TEXT & ~filters.COMMAND,
        #                            self.ask_hours)
        #         ],
        #         self.BOOK_HOURS: [
        #             MessageHandler(filters.TEXT & ~filters.COMMAND,
        #                            self.make_booking)]
        #     },
        #     fallbacks=[]
        # )
#
#         admin_conv_handler = ConversationHandler(
#             entry_points=[
#                 CommandHandler('admin', self.admin_command)
#             ],
#             states={
#                 self.ADMIN_CHECK: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.check_admin_and_ask_bikes_num)
#                 ],
#                 self.BIKES_NUM: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_foreign_phone)
#                 ],
#                 self.FOREIGN_PHONE: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_admin_date)
#                 ],
#                 self.FOREIGN_DATE: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_admin_start)
#                 ],
#                 self.FOREIGN_START: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_admin_end)
#                 ],
#                 self.FOREIGN_END: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.make_foreign_book)
#                 ]
#             },
#             fallbacks=[]
#         )
#         password_reset_handler = ConversationHandler(
#             entry_points=[
#                 CommandHandler(
#                     'reset', self.reset_command_and_ask_email
#                 )
#             ],
#             states={
#                 self.RESET_EMAIL: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.ask_verification_code)
#                 ],
#                 self.VERIFICATION_CODE: [
#                     MessageHandler(filters.TEXT & ~filters.COMMAND,
#                                    self.send_reset_password)
#                 ],
#             },
#             fallbacks=[]
#         )
#
#         application.add_handler(start_handler)
#         application.add_handler(help_handler)
#         application.add_handler(create_conv_handler)
#         application.add_handler(booking_conv_handler)
#         application.add_handler(admin_conv_handler)
#         application.add_handler(password_reset_handler)
#         application.add_handler(unknown_command_handler)
#
#         application.run_polling()
