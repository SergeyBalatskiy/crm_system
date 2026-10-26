# Импортируется модуль который автоматически форматирует обьект под нужные нам требования
import re
# Импортируем модуль который регистрирует кастомный фильтр (кастом-функцию) в самом шаблоне HTML
from django import template

register = template.Library()

@register.filter(name='format_phone')
def format_phone(value):
    if not value:
        return ""
    
    digits = re.sub(r'\D', '', str(value))
    
    if len(digits) == 11 and digits[0] in ('7', '8'):
        return f"+7 ({digits[1:4]}) {digits[4:7]} {digits[7:9]}-{digits[9:11]}"
    
    if len(digits) == 10:
        return f"+7 ({digits[0:3]}) {digits[3:6]} {digits[6:8]}-{digits[8:10]}"
        
    return value 