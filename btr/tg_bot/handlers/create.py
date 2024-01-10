from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _

from btr.orm_utils import check_available_field_as, create_account_as
from btr.tasks.reg_tasks import send_reg_data_from_tg

from ..states.create_account import CreateAccountState
from ..exceptions import (NameOverLengthError, InvalidEmailError,
                          InvalidPhoneError)
from ..validators import validate_name, validate_email, validate_phone_number


class CreateAccount:

    @staticmethod
    async def ask_name(message: Message, state: FSMContext, bot: Bot):
        msg = _(
            '<strong>Create Account</strong>\n\n'
            '<em>Hi! Let\'s create an account!\n'
            'Please, type your Name:</em>'
        )
        await bot.send_message(message.from_user.id, msg)
        await state.set_state(CreateAccountState.regName)

    @staticmethod
    async def ask_username(message: Message, state: FSMContext, bot: Bot):
        name = message.text
        try:
            validate_name(name)
            msg = _(
                '🟢🟢🟢\n\n'
                '👋 <em>Hello,</em> <strong>{name}</strong>!\n'
                '<em>Come up with a username</em>⤵️'
            ).format(name=name)
            await bot.send_message(message.from_user.id, msg)
            await state.update_data(regname=name)
            await state.set_state(CreateAccountState.regUsername)
        except NameOverLengthError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Name length must be less than 40 symbols!\n\n'
                '</strong>\n\n'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(message.from_user.id, msg)

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        username = message.text
        if await check_available_field_as(username):
            try:
                validate_name(username)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Great! Username</em>'
                    ' <strong>{username}</strong><em> is available!</em>\n'
                    '<em>Now, i need your valid</em> ✉️<strong>Email'
                    '</strong>⤵️'
                ).format(username=username)
                await bot.send_message(message.from_user.id, msg)
                await state.update_data(regusername=username)
                await state.set_state(CreateAccountState.regEmail)
            except NameOverLengthError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Username length must be less than 40 symbols!\n\n'
                    '</strong>\n\n'
                    '<em>Try again</em> ⤵️'
                )
                await bot.send_message(message.from_user.id, msg)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Username <em>{username}</em> already exists!'
                '</strong>\n\n'
                '<em>Try another username</em>⤵️'
            ).format(username=username)
            await bot.send_message(message.from_user.id, msg)

    @staticmethod
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        email = message.text
        if await check_available_field_as(email):
            try:
                validate_email(email)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Great! We are almost finished!\n'
                    'All that remains is to enter phone number</em>\n\n'
                    '📝 <strong>Format: +7xxxxxxxxxx</strong>\n\n'
                    '⚠️ <strong>Case sensitive</strong>⤵️'
                )
                await bot.send_message(message.from_user.id, msg)
                await state.update_data(regemail=email)
                await state.set_state(CreateAccountState.regPhone)

            except InvalidEmailError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Invalid email format <em>{email}</em></strong>\n'
                    '\n<em>Check your spelling and try again</em>⤵️'
                ).format(email=email)
                await bot.send_message(message.from_user.id, msg)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>User with email <em>{email}</em> already'
                'exists!</strong>\n\n'
                '<em>Forgot password? Type <strong>/reset</strong>'
                'command\n'
                'Or try again</em>⤵️'
            ).format(email=email)
            await bot.send_message(message.from_user.id, msg)

    @staticmethod
    async def create_account(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        if check_available_field_as(phone):
            try:
                validate_phone_number(phone)
                await state.update_data(regphone=phone)
                reg_data = await state.get_data()
                password = await create_account_as(reg_data)
                send_reg_data_from_tg.delay(
                    reg_data.get('regemail'),
                    reg_data.get('regname'),
                    reg_data.get('regusername'),
                    reg_data.get('regphone'),
                    password,
                )
                msg = _(
                    '🎉🎉🎉 <strong>Account created successfully!</strong>'
                    '🎉🎉🎉\n\n'
                    '<em>All sign in info was send to</em>↙️\n\n'
                    '✉️ {email}'
                ).format(email=reg_data.get('regemail'))
                await bot.send_message(message.from_user.id, msg)
                await state.clear()
            except InvalidPhoneError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Invalid phone format <em>{phone}</em></strong>\n'
                    '\n<em>Check your spelling and try again</em>⤵️'
                ).format(phone=phone)
                await bot.send_message(message.from_user.id, msg)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>User with phone number <em>{email}</em> already'
                'exists!</strong>\n\n'
                '<em>Forgot password? Type <strong>/reset</strong>'
                'command\n'
                'Or try again</em>⤵️'
            ).format(phone=phone)
            await bot.send_message(message.from_user.id, msg)