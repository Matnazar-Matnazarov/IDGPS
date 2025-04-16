from django import template
import re

register = template.Library()


@register.filter
def subtract(value, arg):
    """Ikki son ayirmasini hisoblash"""
    try:
        return float(value or 0) - float(arg or 0)
    except (ValueError, TypeError):
        return 0


@register.filter(name="get_item")
def get_item(dictionary, key):
    """Dictionary'dan key bo'yicha qiymatni olish"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(name="mul")
def multiply(value, arg):
    """
    Multiplies the given value by the argument.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0