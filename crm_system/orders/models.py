from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from profile_user.models import WorkersInfo
from storage.models import StorageInfo
from auth_registration.models import Users

User = get_user_model()

# Данная модель хранит в себе всех клиентов которые хотя бы раз обращались к нам
class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_for_order')
    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=45, db_index=True)

    class Meta:
        # Говорю, что два поля должны быть уникальны в рамках строго этого пользователя!
        unique_together = ('user' , 'phone')

# Данная модель позволяет создать заявку с важными параметрами внутри нее 
class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list_orders')

    # Создаю статус для заказа
    name_category = models.CharField(max_length=100, default='Новый')
    color_category = models.CharField(max_length=100, default='#3498db')
    category_eng = models.CharField(max_length=100, default='new')

    # Тип заказа
    type_of_order = models.CharField(max_length=20)
    
    # Менеджер (кто оформил заявку)
    manager = models.CharField(db_index=True, null=True, blank=True, max_length=100)

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
    deadline = models.DateTimeField(null=True, blank=True)

    # Само поле для JSON-форм и данных внутри неё:
    form_with_order_information = models.JSONField()

    # Булево значение для: СРОЧНО
    important = models.BooleanField(default=False)

    # Указываю предоплату, если галочка была выбрана в самой форме: (Decimalfield чтобы потом
    # добавлять в историю транзакций: ВНЕСЕНИЕ > Прочее > Предоплата)
    prepay = models.DecimalField(decimal_places=0, max_digits=11)

    def __str__(self):
        return f'Статус: {self.name_category}, Менеджер: {self.manager}, ФИО клиента: {self.client.name}, Номер: {self.client.phone}, Название девайса: {self.name_of_device}, Проблема с девайсом: {self.problem_with_device}, Был создан: {self.created_at}, Поле c JSON-формами: {self.form_with_order_information}.'

# Данный класс отвечает за создание услуги, которая связана с опеределеной заявкой на ремонт
class CreateServiceWork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='create_service_work')
    
    # Данное поле отвечает за соединение с УНИКАЛЬНЫМ КЛЮЧОМ определенного заказа
    connected_id = models.ForeignKey(Orders, on_delete=models.CASCADE)

    # Оказанная услуга: (ее название)
    service_provided = models.CharField(max_length=300)

    # Дата оказанной услуги:
    service_was_created = models.DateTimeField(default=timezone.now)

    # Цена оказанной услуги
    service_price = models.DecimalField(decimal_places=0, max_digits=11)

    # ------------------------------------------------------------------
    # Здесь идет запоминание важной информации о товаре в случае отката (удаления работы)
    # ------------------------------------------------------------------

    # Количество используемого товара в ремонте
    quantity_was_used = models.IntegerField()

    # Цена товара в закупке
    detail_buy_price = models.DecimalField(decimal_places=0, max_digits=11, null=True, blank=True)

    # Цена товара в продажу
    detail_retail_price = models.DecimalField(decimal_places=0, max_digits=11, null=True, blank=True)

    # Минимальное количество товара для запоминания
    detail_minimum_items_for_not = models.IntegerField(default=5)

    # Название используемой детали в ремонте
    detail_name_was_used = models.CharField(max_length=120, null=False, blank=False)

    # Поставщик 
    detail_supplier = models.CharField(max_length=120, blank=True, null=True)

    # Индивидуальный код, который запоминается для определенной детали (если она еще есть в БД)
    detail_id = models.IntegerField()

    # Количество на момент закупки
    detail_quantity_was_buyed = models.IntegerField()

    # ------------------------------------------------------------------