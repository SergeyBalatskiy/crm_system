from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from tinymce.models import HTMLField 


# Делаем ссылку на классовую модель пользователя (Текущего)
User = get_user_model()

# Create your models here.
class ServiceInfo(models.Model):
    # Вот здесь САМОЕ ИНТЕРЕСНОЕ И ВЕСЕЛОЕ!!!
    # Когда мы хотим соединить обьект из одной таблицы с другим обьектом
    # из другой таблицы, то обязательно указываем OneToOneField
    # С Аргументами: User,on_delete=models.CASCADE, primary_key=True
    # Потому что таким образом мы гарантируем, что на 1 пользователя будет
    # НЕ больше 1 нового обьекта
    user = models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True, related_name="service_info")
    name_service = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=150, null=True)

    def __str__(self):
        return f'Сервисный центр: {self.name_service}, Адрес:{self.address}, связан с {self.user.get_full_name()}'

# Здесь все то же самое
class WorkersInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    patronymic = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'Cотрудник: {self.name} {self.surname}, связан с {self.user.get_full_name()}'

# Создаю статус категорий
class StatusCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_info')
    name = models.CharField(max_length=100, null=True)
    color = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f'Цвет: {self.color}, Название: {self.name}, Категория: {self.category}, Владелец: {self.user}'

# Создаю информацию о дефолтной форме (уже заполненной в static/txt/.txt)
class DocumentInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_info')
    content = HTMLField()
    name = models.CharField(max_length=110, null=False, blank=False)

    def __str__(self):
        return f'Название: {self.name}, Владелец: {self.user}, текст: {self.content}'

# Функция для внесения дефолтного словаря в поле json_forms
def get_dict_for_json_forms():
    return {
    'sections':[
        {
         'id':'client_info', 
         'title' : 'Клиент',
         'order' : 1,
         'fields' : [{
             'field_key' : 'name',
             'label' : 'Имя клиента',
             'type' : 'select',
             'is_required' : True,
             'hints' : [],
             'order' : 1
         },
         {
            'field_key' : 'phone',
             'label' : 'Телефон',
             'type' : 'select',
             'is_required' : True,
             'hints' : [],
             'order' : 2
         },
         {
             'field_key' : 'telegram',
             'label' : 'Телеграм',
             'type' : 'select',
             'is_required' : False,
             'hints' : [],
             'order' : 3
         }
        ], 
         'custom_forms' : []
    },
    {
        'id':'device_info', 
        'title' : 'Устройство и неисправности',
        'order' : 2,
        'fields' : [{
            'field_key' : 'serial_number',
            'label' : 'Серийный номер',
            'type' : 'select',
            'is_required' : False,
            'order' : 1
         },
         {
            'field_key' : 'type_of_device',
            'label' : 'Тип устройства',
            'type' : 'select',
            'is_required' : False,
            'hints' : ['Телефон', 'Ноутбук', 'Планшет', 'Компьютер'],
            'order' : 2
         },
         {
            'field_key' : 'device_company',
            'label' : 'Марка',
            'type' : 'select',
            'is_required' : False,
            'hints' : [],
            'order' : 3
         },
         {
            'field_key' : 'color',
            'label' : 'Цвет',
            'type' : 'select',
            'is_required' : False,
            'hints' : [],
            'order' : 4
         }
        ], 
        'custom_forms' : []
    },
    {
        'id':'bonus_information', 
        'title' : 'Дополнительная информация',
        'order' : 3,
        'fields' : [{
            'field_key' : 'target_price',
            'label' : 'Ориентировочная цена',
            'type' : 'select',
            'is_required' : False,
            'order' : 1
         },
         {
            'field_key' : 'master',
            'label' : 'Мастер',
            'type' : 'select',
            'is_required' : False,
            'order' : 2
         },
         {
            'field_key' : 'manager',
            'label' : 'Менеджер',
            'type' : 'select',
            'is_required' : False,
            'order' : 3
         },
         {
            'field_key' : 'comment_of_order',
            'label' : 'Комментарий приемщика',
            'type' : 'textarea',
            'is_required' : False,
            'order' : 4
         }
        ], 
        'custom_forms' : []
    }
    ]}

class FormsForOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forms_for_order')
    type_of_order = models.CharField(max_length=100, null=True)
    json_forms = models.JSONField(default=get_dict_for_json_forms)        
    
    def __str__(self):
        return f'Название формы заказа: {self.type_of_order}, Владелец: {self.user}'
