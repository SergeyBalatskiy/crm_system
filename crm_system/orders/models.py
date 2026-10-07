from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from profile_user.models import WorkersInfo

User = get_user_model()

# В случае удаления сотрудника, который связан с этим обьектом, менеджером записывается владелец!
def get_main_user(self):
    ...

class Client(models.Model):
    ...

# Данная модель позволяет создать заявку с важными параметрами внутри нее 
class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list_orders')

    # Статус / Тип заказа
    status = models.CharField(max_length=60, db_index=True)
    type_of_order = models.CharField(max_length=20)
    
    # Менеджер (кто оформил заявку)
    manager = models.ForeignKey(WorkersInfo, db_index=True, on_delete=models.SET(get_main_user))

    # Информация о клиенте: ФИО / Номер телефона
    client_name = models.ForeignKey(Client, db_index=True)
    client_phone = models.ForeignKey(Client, db_index=True)

    # Информация о девайсе (устройстве): Тип устройства / Цвет устройства / Название устройства / Проблема с устройством 
    device_type = models.CharField(max_length=40, db_index=True) # Тип устройства: Телефон, Планшет, Ноутбук и т.д.
    color_of_device = models.CharField(max_length=40, db_index=True)
    name_of_device = models.CharField(max_length=150, db_index=True)
    problem_with_device = models.CharField(max_length=150, db_index=True)

    # Было создано:
    created_at = models.DateTimeField(default=timezone.now)

    # Крайний срок:
    dealdine = models.DateTimeField(null=True, blank=True)

    # Само поле для JSON-форм и данных внутри неё:
    form_with_order_information = models.JSONField()

    def __str__(self):
        return f'Статус: {self.status}, Менеджер: {self.manager}, ФИО клиента: {self.client_name}, Номер: {self.client_phone}, Название девайса: {self.name_of_device}, Проблема с девайсом: {self.problem_with_device}, Был создан: {self.created_at}, Поле c JSON-формами: {self.form_with_order_information}'



    

