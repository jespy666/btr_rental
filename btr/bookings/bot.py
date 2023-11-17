import logging
from telegram import Update
from telegram.ext import (ContextTypes, ApplicationBuilder,
                          CommandHandler, MessageHandler, filters,
                          ConversationHandler)

from btr.bookings.db_handlers import create_user_by_bot_as


class BookingBot:

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    USERNAME, FIRST_NAME, EMAIL, PHONE_NUMBER = range(4)

    def __init__(self, token: str):
        self.token = token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Hi! I am BroTeamRacing booking bot\n'
                 'There are commands that you can type:\n'
                 'To book ride now - /book\n'
                 'To create at account(required for booking) - /createuser\n'
                 'To see help - /help'
        )

    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        help_text = "This is a help message!"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text
        )

    async def create_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please provide your username:'
        )
        return self.USERNAME

    async def ask_username(self, update: Update, context):
        context.user_data['username'] = update.message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Great! Now, please provide your first name.'
        )
        return self.FIRST_NAME

    async def ask_first_name(self, update: Update, context):
        context.user_data['first_name'] = update.message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please provide your email.'
        )
        return self.EMAIL

    async def ask_email(self, update: Update, context):
        context.user_data['email'] = update.message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Finally, please provide your phone number.'
        )
        return self.PHONE_NUMBER

    async def ask_phone_number(self, update: Update, context):
        context.user_data['phone_number'] = update.message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Thank you! All information collected.'
        )
        # You can access collected data via context.user_data
        collected_data = context.user_data
        await create_user_by_bot_as(collected_data)
        return ConversationHandler.END

    def run(self):
        application = ApplicationBuilder().token(self.token).build()

        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler('help', self.help_command)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('create', self.create_command)],
            states={
                self.USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                               self.ask_username)],
                self.FIRST_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_first_name)],
                self.EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                            self.ask_email)],
                self.PHONE_NUMBER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   self.ask_phone_number)]
            },
            fallbacks=[]
        )

        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(conv_handler)

        application.run_polling()
