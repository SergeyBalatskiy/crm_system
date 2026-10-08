from django.urls import path
from .views import *

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    # Путь на указание всех уже созданных заявок + фильтр туда же
    path('', ShowAndFilterOrders.as_view(), name='orders'),
    path('show_form', ShowFormForOrder.as_view(), name='show_form'),
]
