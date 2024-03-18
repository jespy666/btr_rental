from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import html

from django.utils.translation import gettext as _

from btr.orm_utils import AsyncTools
from ..states.create_account import CreateAccountState
from ..utils.handlers import mail_notify
from ..utils.validators import (validate_name, validate_email,
                                validate_phone_number)
from ..utils.decorators import validators
from ..keyboards.kb_cancel import CancelKB


class CreateAccount:

    @staticmethod
    async def ask_name(message: Message, state: FSMContext, bot: Bot):
        user_id = message.from_user.id
        kb = CancelKB().place()
        msg = _(
            '<em><strong>Let\'s create an account!</strong>\n\n'
            'Please, type your <strong>Name</strong> ⤵️</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.set_state(CreateAccountState.regName)

    @staticmethod
    @validators
    async def ask_username(message: Message, state: FSMContext, bot: Bot):
        name = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_name(name)
        msg = _(
            '🟢🟢🟢\n\n'
            '👋 <em>Hello, <strong>{name}</strong>!\n\n'
            'Come up with a username</em> ⤵️'
        ).format(name=html.bold(html.quote(name)))
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(name=name)
        await state.set_state(CreateAccountState.regUsername)

    @staticmethod
    @validators
    async def ask_email(message: Message, state: FSMContext, bot: Bot):
        username = message.text
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_name(username)
        await AsyncTools().check_available_field(username)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Great!</strong>\n\n'
            'Username <strong>{username}</strong> is available!\n\n'
            'Now, i need your valid\n\n ✉️ <strong>Email ⤵️</strong></em>'
        ).format(username=html.bold(html.quote(username)))
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(username=username)
        await state.set_state(CreateAccountState.regEmail)

    @staticmethod
    @validators
    async def ask_phone(message: Message, state: FSMContext, bot: Bot):
        email = message.text.lower()
        user_id = message.from_user.id
        kb = CancelKB().place()
        validate_email(email)
        await AsyncTools().check_available_field(email)
        msg = _(
            '🟢🟢🟢\n\n'
            '<em><strong>Ok!</strong>\n\nWe are almost finished!\n\n'
            'All that remains is to enter phone number\n\n'
            '📝 <strong>Format: +7xxxxxxxxxx</strong>\n\n'
            '⚠️ <strong>Case sensitive</strong> ⤵️</em>'
        )
        await bot.send_message(user_id, msg, reply_markup=kb)
        await state.update_data(email=email)
        await state.set_state(CreateAccountState.regPhone)

    @staticmethod
    @validators
    async def create_account(message: Message, state: FSMContext, bot: Bot):
        phone = message.text
        data = await state.get_data()
        user_id = message.from_user.id
        validate_phone_number(phone)
        await AsyncTools().check_available_field(phone)
        data['phone'] = phone
        data['status'] = _('Newbie')
        password = await AsyncTools().create_account(data)
        data['password'] = password
        data['login'] = data.get('username')
        mail_notify('hello_msg', **data)
        msg = _(
            '🎉🎉🎉\n\n'
            '<em><strong>Account created successfully!</strong>\n\n'
            'All sign in info was send to ↙️\n\n'
            '✉️ <strong>{email}</strong>'
            'You can sign in here ↙️\n\n'
            '<strong>broteamracing.ru/auth/login</strong></em>'
        ).format(email=data.get('email'))
        await bot.send_message(user_id, msg)
        await state.clear()
