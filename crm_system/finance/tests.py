from django.test import TestCase
from itertools import zip_longest
# Create your tests here.
y = [1, 2, 3, 4]
z = ['a', 'b']

# по умолчанию пустые места заполнятся значением None
for i, k in zip_longest(y, z, fillvalue=None):
    if not k:
        print('Нет к!')
    else:
        print(i, k)

