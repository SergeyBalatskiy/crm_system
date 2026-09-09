from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Указываю на путь к СКЛАДУ (Там хранятся все АКТУАЛЬНЫЕ ТОВАРЫ)
    path('', StorageCustomView.as_view(), name='main-storage'),
    # Указываю на путь к СКЛАДУ-ПОСТУПЛЕНИЮ (Там можно добавить новое поступление на склад)
    path('acceptable', StorageAcceptableCustomView.as_view(), name='acceptance-storage'),
    # Указываю на путь к СКЛАДУ-списанию (Там можно изьять товары на складе)
    path('removal-storage', StorageRemovalCustomView.as_view(), name='removal-storage'),
    # Указываю на путь к показу выбора форм на списание гарантийного возврата
    path('removal', FormRemovalCustomView.as_view(), name='removal-form-storage'),   
    # Указываю на путь к показу историй создания/списания товаров на складе
    path('history', StorageHistoryCustomView.as_view(), name='history-storage'),
    # Указываю на путь к показу формы Гарантийного возврата
    path('garanty', StorageGarantyCustomView.as_view(), name='garanty-storage'),   
    # Указываю на путь к обращению чтобы отрбражать авто ответы для подсказок из БД
    path('storage-autocomplete', CountryAutocomplete.as_view(), name='storage-autocomplete'),   
    
]
