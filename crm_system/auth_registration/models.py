from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Users(AbstractUser):
    phone_number = models.CharField(max_length=30, null=False, unique=True)
    email = models.EmailField(unique=True, max_length=254, null=False)

    def __str__(self):
        return f'Пользователь с id:{self.id}, {self.first_name} {self.last_name}'
