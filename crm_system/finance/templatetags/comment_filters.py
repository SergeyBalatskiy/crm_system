import re
from django import template

register = template.Library()

@register.filter(name="format_comment_numbers")
def format_comment_numbers(value):
    if not isinstance(value, str):
        value = str(value)

    def replace_match(match):
        # возвращает автоматически назад значение
        number = match.group(0)
        # Форматирование числа с пробелом
        return f"{int(number):,}".replace(',', ' ')

    # Если найдено число:
    return re.sub(r'\d{4}', replace_match, value)