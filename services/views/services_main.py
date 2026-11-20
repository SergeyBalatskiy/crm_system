from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q, TextField
from django.views import View
from services.models import ServicesInfo
from services.forms import ServicesWorkForm
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
import json
from django.db.models.functions import Cast
from django.shortcuts import render
from django.db.models import Q

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

        # Получаю квери сет всех обьектов
        qs = ServicesInfo.objects.filter(user=request.user)
        formset = ServicesWorkForm(user=request.user)
        fast_search = request.GET.get('fast_search_all', '').strip()
       
        # Поиск по "Быстрому поиску"
        if fast_search:
            # "Переформатирую данные" из инта в текст
            qs = qs.annotate(price_str=Cast('price', output_field=TextField()))
    
            # "Закидываю в фильтр"
            text_q = (
                Q(name_service_work__icontains=fast_search) | 
                Q(price_str__icontains=fast_search) | 
                Q(category__name_category_work__icontains=fast_search))
            # Привязываю к глобальному поиску
            qs=qs.filter(text_q)

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        context = {'service_works' : qs, 'form_services' : formset, 'fast_search_all' : fast_search}
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

            if request.headers.get('HX-Request'):
                msg = 'Новая услуга была успешно создана!'
                print(msg)
                messages.success(request, msg)
                response = HttpResponse()
                response['HX-Redirect'] = reverse('services_work')
                return response                  
        
        except Exception as e:
            return self.htmx_toast_error(f'Ошибка: {e}')
