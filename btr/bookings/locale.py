from django.conf import settings
from django.utils.translation import gettext as _


def locale_month_name_plural(month: str) -> str:
    """Set current language month name plural"""
    if settings.LANGUAGE_CODE == 'ru':
        months = {
            'January': _('Januarys'),
            'February': _('Februarys'),
            'March': _('Marchs'),
            'April': _('Aprils'),
            'May': _('Mays'),
            'June': _('Junes'),
            'July': _('Julys'),
            'August': _('Augusts'),
            'September': _('Septembers'),
            'October': _('Octobers'),
            'November': _('Novembers'),
            'December': _('Decembers'),
        }
        return months.get(month)
    return month


def locale_month_name(month: str) -> str:
    """Set current language month name"""
    if settings.LANGUAGE_CODE == 'ru':
        months = {
            'January': _('January'),
            'February': _('February'),
            'March': _('March'),
            'April': _('April'),
            'May': _('May'),
            'June': _('June'),
            'July': _('July'),
            'August': _('August'),
            'September': _('September'),
            'October': _('October'),
            'November': _('November'),
            'December': _('December'),
        }
        return months.get(month)
    return month
