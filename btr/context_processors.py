from django.conf import settings
from django.utils.translation import gettext as _


def common_context(request):
    """Set general context to templates"""
    return {
        'YANDEX_VERIFICATION_ID': settings.YANDEX_VERIFICATION_ID,
        'title': _(
            'BroTeamRacing - Enduro and Pit-bikes rental in Saint-Petersburg'
        ),
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
    }
