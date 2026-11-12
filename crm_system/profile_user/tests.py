def format_initials(initials):
    if not initials:
        return ""

    index = initials.index(" ")

    format_int = initials[0 : index + 2]

    return format_int + "."


print(format_initials("Иван Андреевич"))
