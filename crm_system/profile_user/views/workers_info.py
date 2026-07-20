from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from profile_user.forms import ServiceInfoForm, WorkersFormSet, DocumentInfoForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from profile_user.models import StatusCategory, DocumentInformation, WorkersInfo


# Класс который включает в себя метод GET и POST для отображения формы и ее принятия
@method_decorator(login_required(), name='dispatch')
class WorkersAddView(TemplateView):
    template_name = 'profile_user/create_workers.html'

    # Здесь активируется функция, которая проходится списком и сохраняет в каждой форме нашего "хозяина"
    def form_valid(self, formset):
        # Беру каждую форму индивидуально и ПРИНУДИТЕЛЬНО останавливаю "автосохранение",
        # чтобы сначала сохранить ссылку на "хозяина", а потом и все остальные данные!
        for form in formset:
            # Если форма заполнена:
            if form.cleaned_data:
                # Остановка сохранения
                workers_info = form.save(commit=False)
                # Запись ссылки на хозяина
                workers_info.user = self.request.user
                # Сохранение всего остального
                workers_info.save()
                
        #  Думаю, будет лучше если здесь добавить кнопку которая сначала позволяет создать только 1
        # человека, потом все это сохраняется (и редиректится) + (показывается текущие сотрудники) и уже только потом позволяет сохранить другого
        return redirect("create_workers")

    # Метод, который показывает нам нашу форму
    def get(self, request, *args, **kwargs):

        # queryset нужен для того, чтобы при обращении к БД, нам в форму не подставлялись
        # уже существующие обьекты...
        # Почему? Потому что я сначала обращаюсь к ФОРМЕ, а в АРГУМЕНЫ ФОРМЫ указываю обьект
        # в виде БАЗЫ ДАННЫХ с данными внутри! ЭТО ОЧЕНЬ ОПАСНО!!! И чтобы такого не было,
        # необходимо явно указать самой "форме, работающей с базой данных", чтобы та не брала
        # у базы данных существующие данные, а просто была пустой!
        formset = WorkersFormSet(queryset=WorkersInfo.objects.none())

        # ХОЧУ ОТМЕТИТЬ ОДИН НЬЮАНС: В БУДУЩЕМ СЛЕДУЕТ ДОБАВИТЬ СЮДА ВЫБОРКУ, ГДЕ У МЕНЯ
        # БУДЕТ В виде словаря отображаться все пользователи созданные

        return render(request, self.template_name,{'workers_formset' : formset})

    # Метод, который принимает нашу форму методом POST на странице
    def post(self, request, *args, **kwargs):

        # Переменная, которая хранит в себе то, с чем придет пользователь, обращаясь к нам
        # с методом пост (введенные данные внутри формы)
        # ЭТО ИМЕННО НЕСКОЛЬКО ФОРМ (МОЖЕТ БЫТЬ)
        formset = WorkersFormSet(data=self.request.POST)

        # Вызываем функцию при правильной валидации
        if formset.is_valid():
            return self.form_valid(formset)

        # Показываем на текущем сайте форму, в случае если она не валидна
        return render(request, self.template_name, {'workers_formset': formset})