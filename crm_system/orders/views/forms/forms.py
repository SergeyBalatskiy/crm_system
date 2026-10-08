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
from profile_user.models import FormsForOrder

# Данный класс отвечает за обращение в БД за получением формы и вывод ее 
# актуальных обьектов (из информации о клиенте, устройстве, прочей информации
@method_decorator([login_required, never_cache], name='dispatch') 
class ShowFormForOrder(View):
    
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

        # Отдаю актуальные формы
        get_forms = FormsForOrder.objects.filter(user=request.user, type_of_order='paid').first()
        section = get_forms.json_forms.get('sections')
        print(section)

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        context = {'form' : get_forms}
        return render(request, 'orders/forms/forms.html', context)

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


