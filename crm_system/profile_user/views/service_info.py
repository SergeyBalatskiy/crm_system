from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.forms import ServiceInfoForm, WorkersFormSet, DocumentInfoForm
from profile_user.models import ServiceInfo
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from profile_user.models import StatusCategory, DocumentInformation

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
        # 1. Получаем существующую запись пользователя из БД
        service_instance = ServiceInfo.objects.filter(user=user).first()

        # 2. Передаем и данные из формы (request.POST), и найденный instance
        form = ServiceInfoForm(request.POST, instance=service_instance)

        if form.is_valid():
            service_info = form.save(commit=False)
            service_info.user = user
            service_info.save()
            return redirect('workers')

        # Если валидация не прошла, возвращаем форму с ошибками
        return render(request, self.template_name, {'service_info': form})