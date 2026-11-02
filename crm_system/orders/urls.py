from django.urls import path
from .views import *

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Путь на указание всех уже созданных заявок + фильтр туда же
    path('', ShowAndFilterOrders.as_view(), name='orders'),
    path('show_form', ShowFormForOrder.as_view(), name='show_form'),
    path('find_client', FindClientInformation.as_view(), name='find_client'),
    path('client_order', ShowClientOrder.as_view(), name='client_order'),
    path('find_worker', FindWorkersInformation.as_view(), name='find_worker'),
    path('create_service_work', ServiceWorkCreate.as_view(), name='create_service_work'),
    # Указываю на путь к обращению за деталямии чтобы отрбражать авто ответы для подсказок из БД
    path('orders_autocomplete', OrdersDetailsAutocomplete.as_view(), name='orders_autocomplete'), 
    # Указываю на путь к обращению за рабочими услугами, чтобы отрбражать авто ответы для подсказок из БД
    path('services_autocomplete', ServicesSelectAutocomplete.as_view(), name='services_autocomplete'), 
    
]
