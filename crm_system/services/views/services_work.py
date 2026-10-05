from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.db.models import Q, TextField, F
from django.views import View
from services.models import ServicesInfo
from services.forms import ServicesWorkForm
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
import json

# Данный класс отвечает за показ всех добавленных услуг и также фильтры(В БУДУЩЕМ!) + возможность создавать новые услуги
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowAndCreateServicesWork(View):

    @staticmethod
    def htmx_toast_error(message):
        print('Сработала функция ерор')
        print(message)
        """Возвращает 204 No Content"""
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'level': 'error',
                'message': message
            }
        })
        return response
    
    def get(self, request, *args, **kwargs):
        # Получаю все созданные ранее услуги в БД:
        
        # Думаю что сюда в будущем нужно будет добавить фильтр
        
        # Передаю также и форму
        formset = ServicesWorkForm(user=request.user)

        get_services = ServicesInfo.objects.filter(user=request.user)

        context = {'service_works' : get_services, 'form_services' : formset}
        return render(request, 'services/services_main.html', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Получаю, формсет
        formset = ServicesWorkForm(request.POST, user=request.user)
        
        try:
            # Валидация формсета
            if not formset.is_valid():
                return self.htmx_toast_error('Необходимо, чтобы все поля были заполнены корректно!')

            # Сохраняю                
            obj = formset.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('services_work')
        
        except Exception as e:
            return self.htmx_toast_error(f'Ошибка: {e}')
