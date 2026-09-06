from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone

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
    created_at = models.DateTimeField(default=timezone.now()) # Дата создания (поступления) товара

    # Функция пред-сохранения айдишника
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.individual_code:
            self.individual_code = self.id
            super().save(update_fields=['individual_code'])

    def __str__(self):
        return f'Название: {self.name_product}, Кол-во: {self.remainder}, связан с {self.user.get_full_name()}'


class HistoryStorageInfo(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_storage')
    type_of_operation_history = models.CharField(max_length=120, null=True, blank=True) # Тип операции? (Поступление, списание, возврат)
    name_product_history = models.CharField(max_length=120, null=True, blank=True) # Название товара
    individual_code_history = models.IntegerField(null=True, blank=True)  # id (Код товара)
    quantity_history = models.IntegerField(null=True, blank=True) # Количество, которое учавствует в операции (Добавление, списание, возврат)
    buy_price_history = models.IntegerField(null=True, blank=True) # Стоимость закупки (1 шт.)
    supplier_history = models.CharField(max_length=120, null=True, blank=True) # Поставщик
    remainder_history = models.IntegerField(null=True, blank=True) # Остаток на складе (После проведения операции)
    time_of_operation_history = models.DateTimeField(null=True, blank=True) # Время проведения операции ("создание"\"списание"\"возврат")
    time_created_history = models.DateTimeField(null=True, blank=True) # Время проведения операции (Появления самого товара)

    def __str__(self):
        return f'История товара: {self.name_product_history}, Кол-во: {self.remainder_history}, связан с {self.user.get_full_name()}'

