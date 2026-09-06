from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.staticfiles import finders
from storage.forms import StorageAcceptableForm
from storage.models import HistoryStorageInfo
from django.contrib import messages
from datetime import datetime


# Данный класс отвечает за показ сайта где можно добавить новые поступления на склад
@method_decorator(login_required(), name='dispatch') 
class StorageHistoryCustomView(TemplateView):

    template_name = 'storage/history-storage.html'

    def get(self, request, *args, **kwargs):

        # Получаю объект из БД для показа уже созданных когда-либо товаров, в том числе актуальных
        storage_history_items = HistoryStorageInfo.objects.filter(
            user=self.request.user
        ).all()

        if storage_history_items:
            return render(request, self.template_name, {"storage_history_items" : storage_history_items })

        return render(request, self.template_name)
                        