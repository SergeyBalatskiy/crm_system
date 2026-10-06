from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.db.models import Q, TextField, F
from django.views import View
from services.models import ServicesInfo, CategoryServicesInfo
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
import json

# Данный класс отвечает за удаление категории / услуги
@method_decorator(login_required(), name='dispatch') 
class DeleteCategoryOrServices(View):

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
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Получаю запрос на удаление (категория / услуга)
        get_services_to_delete = request.POST.get('services')
        get_category_to_delete = request.POST.get('category')

        try:
            if get_services_to_delete:
                ServicesInfo.objects.filter(user=request.user, id=get_services_to_delete).delete()
                print('Удалено!')

                if request.headers.get('HX-Request'):
                    msg = 'Услуга была успешно удалена!'
                    print(msg)
                    messages.success(request, msg)
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('services_work')
                    return response   
            print(get_category_to_delete)
            if get_category_to_delete:
                CategoryServicesInfo.objects.filter(user=request.user, name_category_work=get_category_to_delete).delete()

                if request.headers.get('HX-Request'):
                    msg = 'Категория и услуги были успешно удалены!'
                    print(msg)
                    messages.success(request, msg)
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('services_work')
                    return response   
        
            return redirect('services_work')

        except Exception as e:
            return self.htmx_toast_error(f'Ошибка: {e}')
