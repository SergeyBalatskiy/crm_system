from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class StorageInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage')
    individual_code = models.IntegerField(max_length=100) # Код
    name_product = models.CharField(max_length=120)
    quantity_at_the_purchase = models.IntegerField(max_length=100) # Количество на момент закупки
    supplier = models.CharField(max_length=120, blank=True) # Поставщик
    buy_price = models.IntegerField(max_length=100) # Стоимость закупки (1 шт.)
    retail_price = models.IntegerField(max_length=100) # Цена для продажи (1 шт.)
    minimum_items_for_notification = models.IntegerField(max_length=100, default=10) # Минимальное количество для напоминания
    remainder = models.IntegerField(max_length=100) # Остаток на складе

    def __str__(self):
        return f'Название: {self.name_product}, Кол-во: {self.remainder}, связан с {self.user.get_full_name()}'
