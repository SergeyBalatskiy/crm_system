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

class StatusCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_info')
    name = models.CharField(max_length=100, null=True)
    color = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f'Цвет: {self.color}, Название: {self.name}, Категория: {self.category}, Владелец: {self.user}'
    
class DocumentInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_info')
    content = HTMLField(default='Тут будет текст для документов')
    name = models.CharField(max_length=110, null=False, blank=False)

    def __str__(self):
        return f'Название: {self.name}, Владелец: {self.user}, текст: {self.content}'
    
    
    
