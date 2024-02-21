from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import html

from django.utils.translation import gettext as _

from btr.orm_utils import check_available_field_as, create_account_as
from btr.tasks.users import send_hello_msg

from ..states.create_account import CreateAccountState
from ..utils.exceptions import (NameOverLengthError, InvalidEmailError,
                                InvalidPhoneError)
from ..utils.validators import (validate_name, validate_email,
                                validate_phone_number)
from ..keyboards.kb_cancel import CancelKB


class CreateAccount:

    @staticmethod
    async def ask_name(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<strong>Create Account</strong>\n\n'
            '<em>Let\'s create an account!\n'
            'Please, type your Name ⤵️</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(CreateAccountState.regName)

    @staticmethod
    async def ask_username(message: Message, state: FSMContext, bot: Bot):
        name = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            validate_name(name)
            msg = _(
                '🟢🟢🟢\n\n'
                '👋 <em>Hello,</em> <strong>{name}</strong>!\n\n'
                '<em>Come up with a username</em> ⤵️'
            ).format(name=html.bold(html.quote(name)))
            await bot.send_message(user_id, msg, reply_markup=kb)
            await state.update_data(regname=name)
            await state.set_state(CreateAccountState.regUsername)
        except NameOverLengthError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Name length must be less than 40 symbols!\n\n'
                '</strong>'
                '<em>Try again</em> ⤵️'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        username = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        if await check_available_field_as(username):
            try:
                validate_name(username)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Great! Username</em>'
                    ' <strong>{username}</strong><em> is available!</em>\n'
                    '<em>Now, i need your valid</em> ✉️ <strong> Email'
                    '</strong> ⤵️'
                ).format(username=html.bold(html.quote(username)))
                await bot.send_message(user_id, msg, reply_markup=kb)
                await state.update_data(regusername=username)
                await state.set_state(CreateAccountState.regEmail)
            except NameOverLengthError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Username length must be less than 40 symbols!\n\n'
                    '</strong>'
                    '<em>Try again</em> ⤵️'
                )
                await bot.send_message(user_id, msg, reply_markup=kb)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>Username <em>{username}</em> already exists!'
                '</strong>\n\n'
                '<em>Try another username</em> ⤵️'
            ).format(username=html.bold(html.quote(username)))
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        email = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        if await check_available_field_as(email):
            try:
                validate_email(email)
                msg = _(
                    '🟢🟢🟢\n\n'
                    '<em>Great! We are almost finished!\n'
                    'All that remains is to enter phone number</em>\n\n'
                    '📝 <strong>Format: +7xxxxxxxxxx</strong>\n\n'
                    '⚠️ <strong>Case sensitive</strong> ⤵️'
                )
                await bot.send_message(user_id, msg, reply_markup=kb)
                await state.update_data(regemail=email)
                await state.set_state(CreateAccountState.regPhone)

            except InvalidEmailError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Invalid email format <em>{email}</em></strong>\n'
                    '\n<em>Check your spelling and try again</em> ⤵️'
                ).format(email=email)
                await bot.send_message(user_id, msg, reply_markup=kb)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>User with email <em>{email}</em> already '
                'exists!</strong>\n\n'
                '<em>Forgot password? Type <strong>/reset</strong>'
                'command\n'
                'Or try again</em> ⤵️'
            ).format(email=email)
            await bot.send_message(user_id, msg, reply_markup=kb)

    @staticmethod
    async def create_account(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        if check_available_field_as(phone):
            try:
                validate_phone_number(phone)
                await state.update_data(regphone=phone)
                reg_data = await state.get_data()
                password = await create_account_as(reg_data)
                send_hello_msg.delay(
                    reg_data.get('regemail'),
                    reg_data.get('regname'),
                    reg_data.get('regusername'),
                    password,
                )
                msg = _(
                    '🎉🎉🎉\n\n'
                    '<strong>Account created successfully!</strong>\n\n'
                    '<em>All sign in info was send to</em> ↙️\n\n'
                    '✉️ {email}'
                ).format(email=reg_data.get('regemail'))
                await bot.send_message(user_id, msg)
                await state.clear()
            except InvalidPhoneError:
                msg = _(
                    '🔴🔴🔴\n\n'
                    '<strong>Invalid phone format <em>{phone}</em></strong>\n'
                    '\n<em>Check your spelling and try again</em> ⤵️'
                ).format(phone=phone)
                await bot.send_message(user_id, msg, reply_markup=kb)
        else:
            msg = _(
                '🔴🔴🔴\n\n'
                '<strong>User with phone number <em>{phone}</em> already '
                'exists!</strong>\n\n'
                '<em>Forgot password? Type <strong>/reset</strong>'
                'command\n'
                'Or try again</em> ⤵️'
            ).format(phone=phone)
            await bot.send_message(user_id, msg, reply_markup=kb)
