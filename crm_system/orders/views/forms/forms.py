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

    def get_dict_for_json_forms():
        return {
        'sections':[
            {
            'id':'client_info', 
            'title' : 'Клиент',
            'order' : 1,
            'fields' : [{
                'field_key' : 'name',
                'label' : 'Имя клиента',
                'type' : 'select',
                'is_required' : True,
                'hints' : [],
                'order' : 1
            },
            {
                'field_key' : 'phone',
                'label' : 'Телефон',
                'type' : 'select',
                'is_required' : True,
                'hints' : [],
                'order' : 2
            },
            {
                'field_key' : 'telegram',
                'label' : 'Телеграм',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 3
            }
            ], 
            'custom_forms' : []
        },
        {
            'id':'device_info', 
            'title' : 'Устройство и неисправности',
            'order' : 2,
            'fields' : [{
                'field_key' : 'serial_number',
                'label' : 'Серийный номер',
                'type' : 'select',
                'is_required' : False,
                'order' : 1
            },
            {
                'field_key' : 'type_of_device',
                'label' : 'Тип устройства',
                'type' : 'select',
                'is_required' : False,
                'hints' : ['Телефон', 'Ноутбук', 'Планшет', 'Компьютер'],
                'order' : 2
            },
            {
                'field_key' : 'device_company',
                'label' : 'Марка',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 3
            },
            {
                'field_key' : 'color',
                'label' : 'Цвет',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 4
            }
            ], 
            'custom_forms' : []
        },
        {
            'id':'bonus_information', 
            'title' : 'Дополнительная информация',
            'order' : 3,
            'fields' : [{
                'field_key' : 'target_price',
                'label' : 'Ориентировочная цена',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 1
            },
            {
                'field_key' : 'master',
                'label' : 'Мастер',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 2
            },
            {
                'field_key' : 'manager',
                'label' : 'Менеджер',
                'type' : 'select',
                'is_required' : False,
                'hints' : [],
                'order' : 3
            },
            {
                'field_key' : 'comment_of_order',
                'label' : 'Комментарий приемщика',
                'type' : 'textarea',
                'is_required' : False,
                'hints' : [],
                'order' : 4
            }
            ], 
            'custom_forms' : []
        }
        ]}

    def get(self, request, *args, **kwargs):

        # Отдаю актуальные формы
        get_forms = FormsForOrder.objects.filter(user=request.user, type_of_order='paid').first()
        section = get_forms.json_forms.get('sections')
        # Отдается информация формы о клиенте
        client_info=section[0]
        # Информация о устройстве (поля)
        device_info=section[1]
        # Отдается информация дополнительная
        bonus_information=section[2]

        # Тот обькт, что я выбрал раньше, я применяю к нему действующие фильтры
        context = {'client_info' : client_info, 'device_info' : device_info, 'bonus_information' : bonus_information}
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


