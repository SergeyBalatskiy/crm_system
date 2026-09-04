from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.staticfiles import finders
from storage.forms import StorageAcceptableForm
from storage.models import StorageInfo
from django.contrib import messages
from datetime import datetime


# Данный класс отвечает за показ сайта где можно добавить новые поступления на склад
@method_decorator(login_required(), name='dispatch') 
class StorageHistoryCustomView(TemplateView):

    template_name = 'storage/history-storage.html'
        
    def get(self, request, *args, **kwargs):

        # Здесь мне нужно получить всю базу внесения/списания товаров из БД HistoryStorageInfo

        # А также создать новый обьект в БД HistoryStorageInfo когда "вносят" новый товар на склад и когда его списывают
        ...
        # HistoryStorageInfo