from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from orders.models import Client
from services.forms import ServicesWorkForm
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timedelta
import json
from django.db.models.functions import Cast
from django.shortcuts import render
from profile_user.models import WorkersInfo
from django.db.models import Q, Value
from django.db.models.functions import Concat

# Данный класс отвечает за показ и изменение категории статуса заказа
@method_decorator([login_required, never_cache], name='dispatch') 
class ChangeStatusOrder(View):

    def get(self, request, *args, **kwargs):
        ...

     
    def post(self, request, *args, **kwargs):
        ...