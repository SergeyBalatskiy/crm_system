from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Главное хранилище историй транзакций (всех)
class FinanceHistoryInfo(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='finance')

    class TypeOfOperation(models.TextChoices): # Класс "тип операции" (внесение / списание)
        INCOME = 'Поступление', 'Поступление'
        OUTCOME = 'Исход', 'Исход'

    type_of_operation = models.CharField(
            max_length=15,
            choices=TypeOfOperation.choices
        ) # Тип события: Поступление (in) / Списание (out)

    class CategoryOfOperation(models.TextChoices): # Категория операции (Покупка, Гарантийный возврат, Прочее...)
        SALE = 'Продажа', 'Продажа'
        BUY = 'Покупка', 'Покупка'
        WARRANTY = 'Гарантийный возврат', 'Гарантийный возврат'
        OTHER = 'Прочее', 'Прочее'
    
    category_of_operation = models.CharField(
        max_length=22, choices=CategoryOfOperation.choices
        ) # Тип операции: Продажа товара / Гарантийное списание / Прочие расходы
    
    number_in_the_operation = models.DecimalField(max_digits=11, decimal_places=0) # Число (сумма), которая фигурирует в операции (с копейками)
    created_at = models.DateTimeField(default=timezone.now) # Дата создания операции
    comment = models.CharField(null=True, blank=True, max_length=255) # Комментарий к операции (Если нужен)

    def __str__(self):
        return f'Категория операции: {self.category_of_operation}, Сумма: {self.number_in_the_operation}, связан с {self.user.get_full_name()}'

# Основной денежный счет в сервисе
class CashAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="cash_account")
    money_balance = models.DecimalField(max_digits=11, decimal_places=2, default=0.00) # Денежный баланс 
