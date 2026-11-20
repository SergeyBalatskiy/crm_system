prepay_amount = "".replace(" ", "").replace("\xa0", "").strip()
if not prepay_amount.isdigit():
    prepay_amount = 0

print(prepay_amount)
