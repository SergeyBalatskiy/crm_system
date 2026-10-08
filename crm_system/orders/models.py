from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from profile_user.models import WorkersInfo
from auth_registration.models import Users

User = get_user_model()

# В случае удаления сотрудника, который связан с этим обьектом, менеджером записывается владелец!
def get_main_user(request):
    get_main_user = Users.objects.filter(user=request.user)
    return f'{get_main_user.firs_name} {get_main_user.last_name}'

def return_deleted_info():
    return 'Пользователь был удален'

# Данная модель хранит в себе всех клиентов которые хотя бы раз обращались к нам
class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_for_order')
    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)

    class Meta:
        # Говорю, что два поля должны быть уникальны в рамках строго этого пользователя!
        unique_together = ('user' , 'phone')

# Данная модель позволяет создать заявку с важными параметрами внутри нее 
class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list_orders')

    # Статус / Тип заказа
    status = models.CharField(max_length=60, db_index=True)
    type_of_order = models.CharField(max_length=20)
    
    # Менеджер (кто оформил заявку)
    manager = models.ForeignKey(WorkersInfo, db_index=True, on_delete=models.PROTECT)

    # Информация о клиенте: ФИО / Номер телефона
    client= models.ForeignKey(Client, models.PROTECT, related_name='client_order')
    
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



    

