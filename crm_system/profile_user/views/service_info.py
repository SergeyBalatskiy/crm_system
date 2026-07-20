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

    # Сохранение информации о сервисе 
    def form_valid(self, form):
        service_info = form.save(commit=False)
        service_info.user = self.request.user
        service_info.save()
        return redirect('workers_info')

    # Метод, который показывает нам нашу форму
    def get(self, request, *args, **kwargs):

        # GET запрос для показа формы в 2 вариантах: если данные есть, и если их нет!
        user = self.request.user
        if ServiceInfo.objects.filter(user = user).exists():
            service_info = ServiceInfoForm(instance=ServiceInfo.objects.filter(user = user))
        else:
            service_info = ServiceInfoForm()
        return render(request, self.template_name, {'service_info' : service_info})

    # Метод, который принимает нашу форму методом POST на странице
    def post(self, request, *args, **kwargs):

        formset = ServiceInfoForm(self.request.POST)

        # Вызываем функцию при правильной валидации
        if formset.is_valid():
            return self.form_valid(formset)

        # Показываем на текущем сайте форму, в случае если она не валидна
        return render(request, self.template_name, {'service_info' : formset})
