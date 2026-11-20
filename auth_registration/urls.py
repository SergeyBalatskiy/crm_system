from django.urls import path
from .views import *

urlpatterns = [
    # Ргеистрация пользователя
    path('register/', RegisterView.as_view(), name='registration'),
    # Создание пользователя
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', ShowForm.as_view(), name='auth')
]
