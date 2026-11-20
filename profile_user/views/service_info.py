from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.forms import ServiceInfoForm
from profile_user.models import ServiceInfo
from django.contrib import messages

# Класс который включает в себя метод GET и POST для отображения формы и ее принятия
@method_decorator(login_required(), name='dispatch')
class ServiceInfoView(TemplateView):
    template_name = 'profile_user/service_info.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        service_instance = ServiceInfo.objects.filter(user=user).first()
        service_info = ServiceInfoForm(instance=service_instance)
        return render(request, self.template_name, {'service_info': service_info})

    def post(self, request, *args, **kwargs):
        user = request.user
        service_instance = ServiceInfo.objects.filter(user=user).first()
        form = ServiceInfoForm(request.POST, instance=service_instance)

        if form.is_valid():

            if not form.has_changed():
                messages.error(request, 'Изменений не обнаружено.')
                return redirect('service_info')

            try:
                service_info = form.save(commit=False)
                service_info.user = user
                service_info.save()
                messages.success(request, 'Информация о сервисе успешно сохранена!')
                return redirect('service_info')
            
            except Exception as e:
                messages.error(request, f'Ошибка типа: {e}.')
                return redirect('service_info')

        # Если валидация не прошла, возвращаем форму с ошибками
        return redirect('service_info')