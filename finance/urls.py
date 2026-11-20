from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Показ основного баланса и истории операций
    path('', MainCashAndHistoryView.as_view(), name='main_cash'),
    # Продажа товара
    path('sell', InsertCashInBalance.as_view(), name='insert_cash'),
    # Указываю на путь к обращению чтобы отображать авто ответы для подсказок из БД 
    path('finance-autocomplete', CountryAutocomplete.as_view(), name='finance-autocomplete'),   
    # Указываю на путь к обращению чтобы отображать саму форму на поступление финансов (Прочее)
    path('sell-other', SellFinanceCustomView.as_view(), name='sell-other'),   
    # Указываю на путь к обращению чтобы отображать саму форму на уход финансов (Прочее)
    path('buy-other', BuyFinanceCustomView.as_view(), name='buy-other'),   
    # Указываю на путь к обращению за получением ОДНОЙ из 2-х форм
    path('other-transanction', ShowOthersCustomView.as_view(), name='other_transaction'),  
    
]
