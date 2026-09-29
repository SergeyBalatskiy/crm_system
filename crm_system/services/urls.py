from django.urls import path
from .views import *

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Путь на указание созданных уже услуг + создание услуг
    path('', ShowAndCreateServicesWork.as_view(), name='services_work'),
]
