from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    """Get canonical url from request."""
    request = context.get('request')
    if request:
        return request.build_absolute_uri(
            request.path
        ).replace('http://', 'https://')
    return ''
