from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Указываю на путь к СКЛАДУ (Там хранятся все АКТУАЛЬНЫЕ ТОВАРЫ)
    path('storage', StorageCustomView.as_view(), name='main-storage'),
    # Указываю на путь к СКЛАДУ-ПОСТУПЛЕНИЮ (Там можно добавить новое поступление на склад)
    path('storage/acceptable', StorageAcceptableCustomView.as_view(), name='acceptance-storage'),
    # Указываю на путь к СКЛАДУ-ИЗЬЯТИЮ (Там можно изьять товары на складе)
    path('storage/removal', StorageRemovalCustomView.as_view(), name='removal-storage'),
]
