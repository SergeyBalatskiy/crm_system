from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Показ основного баланса и истории операций
    path('', MainCashView.as_view(), name='main_cash'),
    # Продажа товара
    path('sell', InsertCashInBalance.as_view(), name='insert_cash'),
    # Указываю на путь к обращению чтобы отрбражать авто ответы для подсказок из БД 
    path('finance-autocomplete', CountryAutocomplete.as_view(), name='finance-autocomplete'),   
]
