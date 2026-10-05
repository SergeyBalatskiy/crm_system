from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Этот класс позволяет создавать новую категорию оказания услуги
class CategoryServicesInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_services')
    name_category_work = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return f'{self.name_category_work}'

# Данная модель позволяет создать в services услугу которая включает в себя цену, название, категорию оказания услуги
class ServicesInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    name_service_work = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=11, decimal_places=0)
    category = models.ForeignKey(CategoryServicesInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f'Название: {self.name_service_work}, цена: {self.price}, категория: {self.category}, связан с {self.user.get_full_name()}'
