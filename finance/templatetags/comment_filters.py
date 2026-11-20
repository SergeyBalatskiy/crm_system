import re
from django import template

register = template.Library()

@register.filter(name='format_comment_numbers')
def format_comment_numbers(value):
    if not value:
        return ""
    
    def replace_num(match):
        num_str = match.group(0)
        if len(num_str) <= 3:
            return num_str
        try:
            return f"{int(num_str):,}".replace(",", " ")
        except ValueError:
            return num_str

    return re.sub(r'\d+', replace_num, str(value))