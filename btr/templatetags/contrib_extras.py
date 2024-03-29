from django import template
import datetime


register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    """
    Get the canonical URL from the request.

    Args:
        context (dict): A dictionary containing the context data.

    Returns:
        str: The canonical URL with 'https://' protocol.
    """
    request = context.get('request')
    if request:
        return request.build_absolute_uri(
            request.path
        ).replace('http://', 'https://')
    return ''


@register.filter
def ru_month_genitive(date: datetime.date) -> str:
    """
    Filter to return the genitive form of the month name in Russian.

    Args:
        date (datetime.date): The input date.

    Returns:
        str: The genitive form of the month name.
    """
    months_genitive = {
        1: "Января",
        2: "Февраля",
        3: "Марта",
        4: "Апреля",
        5: "Мая",
        6: "Июня",
        7: "Июля",
        8: "Августа",
        9: "Сентября",
        10: "Октября",
        11: "Ноября",
        12: "Декабря",
    }
    return months_genitive[date.month]
