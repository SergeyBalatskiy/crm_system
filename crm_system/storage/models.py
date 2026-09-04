from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class StorageInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage')
    individual_code = models.IntegerField(null=True, blank=True) # Код
    name_product = models.CharField(max_length=120)
    quantity_at_the_purchase = models.IntegerField() # Количество на момент закупки
    supplier = models.CharField(max_length=120, blank=True) # Поставщик
    buy_price = models.IntegerField() # Стоимость закупки (1 шт.)
    retail_price = models.IntegerField() # Цена для продажи (1 шт.)
    minimum_items_for_notification = models.IntegerField(default=5) # Минимальное количество для напоминания
    remainder = models.IntegerField(null=True, blank=True) # Остаток на складе

    # Функция пред-сохранения айдишника
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.individual_code:
            self.individual_code = self.id
            super().save(update_fields=['individual_code'])

    def __str__(self):
        return f'Название: {self.name_product}, Кол-во: {self.remainder}, связан с {self.user.get_full_name()}'
