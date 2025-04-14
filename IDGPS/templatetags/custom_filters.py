from django import template

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
    return dictionary.get(key, None)
