# store/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Return the value for the given key in a dictionary, defaulting to 0 if not found."""
    return dictionary.get(str(key), 0)

@register.filter(name='multiply')
def multiply(value, arg):
    """Return the result of multiplying value by arg."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0
