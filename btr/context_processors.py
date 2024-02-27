from django.conf import settings


def common_context(request):
    """Set general context to templates"""
    return {
        'YANDEX_VERIFICATION_ID': settings.YANDEX_VERIFICATION_ID,
    }
