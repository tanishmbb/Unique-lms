from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    """Return the basename of a file path."""
    if not value:
        return ''
    return os.path.basename(value)
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
