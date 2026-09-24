from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    path('', MainCashView.as_view(), name='main_cash'),
]
