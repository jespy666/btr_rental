from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.utils.translation import gettext as _

from functools import wraps
from collections import OrderedDict

from ..keyboards.kb_cancel import CancelKB
from . import exceptions as e


def validators(func):
    """Validate all incorrect or wrong user input data"""

    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, bot: Bot,
                      *args, **kwargs):
        data = await state.get_data()
        ordered_data = OrderedDict(data)
        kb_reply = next((
            data[k] for k in reversed(ordered_data.keys())
            if k.endswith('_kb')
        ), None)
        user_id = message.from_user.id
        kb = CancelKB().place()
        try:
            return await func(message, state, bot, *args, **kwargs)
        except e.WrongStatus:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Invalid status!</strong></em>\n\n'
            )
            msg2 = _(
                '<em>Choose new status from options ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.UserAlreadyExists:
            login = message.text
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>User with data ↙️\n\n'
                '{login}\n\nAlready exists!</strong>\n\n'
                'Forgot password?\n'
                'Type <strong>/reset</strong> command!\n\n'
                'Or try another data ⤵️</em>'
            ).format(login=login)
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.UserDoesNotExists:
            login = message.text
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>User with data ↙️\n\n'
                '{login}\n\nDoes not exists!</strong>\n\n'
                'Do not have an account?\n'
                'Type <strong>/create</strong> command!\n\n'
                'Or try another data ⤵️</em>'
            ).format(login=login)
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.NotExistedId:
            pk = data.get('pk')
            msg = _(
                '🔴🔴🔴\n\n'
                '<em>Booking <strong>#{pk}</strong> does not exists!\n</em>'
            ).format(pk=pk if pk else message.text)
            await bot.send_message(user_id, msg, reply_markup=kb)
            if kb_reply:
                msg2 = _(
                    '<em>Please select ID from the options below ⤵️</em>'
                )
                await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.InvalidIDFormat:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>ID must be integer!</strong>\n</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            if kb_reply:
                msg2 = _(
                    '<em>Please select ID from the options below ⤵️</em>'
                )
                await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.NameOverLength:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Length must be less than 40 symbols!\n\n'
                '</strong>Try again ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.InvalidEmailFormat:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Invalid email format!</strong>\n\n'
                'Check your spelling and try again ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.InvalidPhoneFormat:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Invalid phone format!</strong>\n\n'
                '📝 <strong>Format: +7XXXXXXXXXX</strong>\n\n'
                'Check your spelling and try again ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.WrongBikesCount:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em>Bikes count must be at <strong>1 - 4</strong>!\n\n</em>'
            )
            msg2 = _(
                '<em>Choose bikes from options ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.PastTense:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Date can\'t be in past!</strong>\n\n'
                'Choose another date ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.WrongHoursFormat:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Hours must be integer!</strong></em>'
            )
            msg2 = _(
                '<em>Choose hours from options ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.InvalidDate:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Invalid date format!</strong>\n\n'
                '<strong>📆 Format: YYYY-MM-DD\n\n⚠️ Type with \'-\' ⤵️\n\n'
                '</strong>Check your spelling and try again ⤵️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.InvalidTimeFormat:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Invalid time format!</strong></em>'
            )
            msg2 = _('<em>Choose available time from options ⤵️</em>')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.TimeIsNotAvailable:
            slots = data.get('slots')
            start = data.get('start')
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>This time already booked!</strong>\n\n'
                'Available time slots ↙️\n\n<strong>{slots}</strong>\n\n</em>'
            ).format(slots=slots)
            if start:
                msg2 = _(
                    '<em>Your start time ↙️\n\n<strong>{start}</strong>\n\n'
                    'Choose hours from options ⤵️</em>'
                ).format(start=start)
            else:
                msg2 = _(
                    '<em>Choose time from options ⤵️</em>'
                )
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.EndBiggerStart:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>The start time must be before the end!\n\n'
                '</strong></em>'
            )
            msg2 = _('<em>Choose hours from options ⤵️</em>')
            await bot.send_message(user_id, msg, reply_markup=kb)
            await bot.send_message(user_id, msg2, reply_markup=kb_reply)
        except e.CodesCompareError:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Wrong verification code!</strong>\n\n'
                '⚠️ Case sensitive!\n\n'
                'Try again</em> ⤵️'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
        except e.WrongPassword:
            msg = _(
                '🔴🔴🔴\n\n'
                '<em><strong>Wrong password!</strong>\n\n'
                'If you have lost access to your account,\n'
                'select <strong>/reset</strong> command\n\n'
                'Or type password again ↙️</em>'
            )
            await bot.send_message(user_id, msg, reply_markup=kb)
    return wrapper
