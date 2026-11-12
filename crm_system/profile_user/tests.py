# Отвечает за превращение числа в пропись
from num2words import num2words


def number_in_words(number):
    if not number:
        return ""

    number_text = num2words(number, lang="ru")

    return number_text.capitalize()


print(number_in_words(1000))
