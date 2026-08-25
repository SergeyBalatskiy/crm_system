from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.forms import WorkersFormSet
from profile_user.models import WorkersInfo


# Класс который включает в себя метод GET и POST для отображения формы и ее принятия
@method_decorator(login_required(), name='dispatch')
class WorkersAddView(TemplateView):
    template_name = 'profile_user/workers.html'

    # Функция, которая отвечает за удаление сотрудника из БД
    def delete_worker(self, name, surname):
        delete_worker = WorkersInfo.objects.filter(
            user=self.request.user, name = name, surname = surname
        ).first()
            
        delete_worker.delete()
        return redirect("workers")


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
        return redirect("workers")

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

        # Получаю объект из БД для показа уже "активных" сотрудников
        workers_information = WorkersInfo.objects.filter(
            user=self.request.user
        ).all()

        if workers_information:
            return render(request, self.template_name,{'workers_formset' : formset, "workers_information" : workers_information })

        return render(request, self.template_name,{'workers_formset' : formset})

    # Метод, который принимает нашу форму методом POST на странице
    def post(self, request, *args, **kwargs):
        
        # Имя и фамилия на удаление
        delete_name = request.POST.get('delete_name')
        delete_surname = request.POST.get('delete_surname')
        # Вызов функции на удаление
        if delete_name and delete_surname:
            return self.delete_worker(delete_name, delete_surname)

        # Переменная, которая хранит в себе то, с чем придет пользователь, обращаясь к нам
        # с методом пост (введенные данные внутри формы)
        # ЭТО ИМЕННО НЕСКОЛЬКО ФОРМ (МОЖЕТ БЫТЬ)
        formset = WorkersFormSet(data=self.request.POST)
        # Вызываем функцию при правильной валидации
        if formset.is_valid():
            return self.form_valid(formset)

        # Показываем на текущем сайте форму, в случае если она не валидна
                # Получаю объект из БД для показа уже "активных" сотрудников
        workers_information = WorkersInfo.objects.filter(
            user=self.request.user
        ).all()
        return render(request, self.template_name, {'workers_formset': formset, "workers_information" : workers_information})
    
