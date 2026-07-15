from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import path
from .forms import ServiceInfoForm, WorkersFormSet, DocumentInfoForm
from .models import WorkersInfo
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import StatusCategory
from tinymce.models import HTMLField 

# Показывает сам профиль пользователя
@method_decorator(login_required(), name='dispatch')
class UserProfileView(TemplateView):
    template_name = 'profile_user/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

# Показывает формы для названия сервиса и адрес    
@method_decorator(login_required(), name='dispatch')
class ServiceSetupView(TemplateView):
    template_name = 'profile_user/service_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['service_info'] = ServiceInfoForm()
        return context

# При корректных данных идет дальше и приходит
# к показу ServiceSetupView
class CreateServiceInfoView(CreateView):
    form_class = ServiceInfoForm
    template_name = 'profile_user/service_info.html'

    def form_valid(self, form):
        service_info = form.save(commit=False)
        
        service_info.user = self.request.user

        service_info.save()

        return redirect('create_workers')

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
                
        # НА САМОМ ДЕЛЕ МОЖНО СДЕЛАТЬ ТАКУЮ ЛОГИКУ, ЧТО У МЕНЯ СНАЧАЛА ПРОИСХОДИТ РЕДИРЕКТ, А ЕСЛИ
        # Я ХОЧУ СОЗДАТЬ НОВОГО ПОЛЬЗОВАТЕЛЯ, ТО СНАЧАЛА НАЖИМАЮ НА КНОПКУ, А ПОТОМ ТОЛЬКО СОЗДАЮ!
        return redirect("create_workers")

    # Метод, который показывает нам нашу форму
    def get(self, *args, **kwargs):

        # queryset нужен для того, чтобы при обращении к БД, нам в форму не подставлялись
        # уже существующие обьекты...
        # Почему? Потому что я сначала обращаюсь к ФОРМЕ, а в АРГУМЕНЫ ФОРМЫ указываю обьект
        # в виде БАЗЫ ДАННЫХ с данными внутри! ЭТО ОЧЕНЬ ОПАСНО!!! И чтобы такого не было,
        # необходимо явно указать самой "форме, работающей с базой данных", чтобы та не брала
        # у базы данных существующие данные, а просто была пустой!
        formset = WorkersFormSet(queryset=WorkersInfo.objects.none())
        return self.render_to_response({'workers_formset' : formset})

    # Метод, который принимает нашу форму методом POST на странице
    def post(self, *args, **kwargs):

        # Переменная, которая хранит в себе то, с чем придет пользователь, обращаясь к нам
        # с методом пост (введенные данные внутри формы)
        # ЭТО ИМЕННО НЕСКОЛЬКО ФОРМ (МОЖЕТ БЫТЬ)
        formset = WorkersFormSet(data=self.request.POST)

        # Вызываем функцию при правильной валидации
        if formset.is_valid():
            return self.form_valid(formset)

        # Показываем на текущем сайте форму, в случае если она не валидна
        return self.render_to_response({'workers_formset': formset})

# Этот класс отвечает за показ категорий (так и дефолтных), а также и добавляет возможность
# добавлять новые категории/изменять их.
@method_decorator(login_required(), name='dispatch')
class ShowCategoriesView(TemplateView):
    template_name = 'profile_user/categories.html'
    # Метод POST отвечает за принятие формы и ее изменение
    def post(self, *args, **kwargs):
        # Принимаем id этой конкретного статуса чтобы ее изменить
        status_id = self.request.POST.get('id')
        # Принимаем название, цвет, категорию
        name = self.request.POST.get('name')
        color = self.request.POST.get('color')
        category = self.request.POST.get('category')
        # Если айдишник категории есть, значит пользователь хочет работать с тем, что у него
        # уже есть!

        # Здесь я получаю информацию о том, какая кнопка нажата в 
        # <button type="submit" name="action" value="???" id="???"
        action = self.request.POST.get('action')

        # Если "action" у меня "delete":
        if action == 'delete':
            # Сначала беру обьект
            status = get_object_or_404(StatusCategory, id = status_id, user = self.request.user)
            # Потом удаляю
            status.delete()
            return redirect('categories')

        # Если айдишник есть у категории (то есть она была создана ранее а сейчас подвергается)
        # изменению, то...
        if status_id:
            # Получаю именно тот статус, который мне нужен из базы данных по строгим фильтрам
            status = get_object_or_404(StatusCategory, id = status_id, user = self.request.user)
            # Изменяю имя, цвет, категорию
            status.name = name
            status.color = color
            status.category = category
            # Сохраняю
            status.save()
            return redirect('categories')
        # А если нету айдишника, то создаю!
        else:
            # Создаю обьект
            StatusCategory.objects.create(name = name, color = color, category = category, user = self.request.user)
            return redirect('categories')

    # Данный метод работает у меня "вместо метода GET". Так как я его явно не указал, то
    # Именно он и будет отвечать у меня за отображение всей важной логики!
    def get_context_data(self, **kwargs):
        # Если у пользователя БОЛЬШЕ 1 категории (то есть есть еще что-то помимо НОВОЙ категории)
        # то я ему их/её показываю
        context = super().get_context_data(**kwargs)
        context['in_process'] = StatusCategory.objects.filter(category = "in_process", user = self.request.user)
        context['finished'] = StatusCategory.objects.filter(category="finished", user = self.request.user)
        context['success'] = StatusCategory.objects.filter(category="success", user = self.request.user)
        context['deferred'] = StatusCategory.objects.filter(category="deferred", user = self.request.user)

        # ВНИМАНИЕ!!! МЕТОД get_context_data(self, **kwargs): ДОЛЖЕН ОТДАВАТЬ ТОЛЬКО СЛОВАРЬ!
        # НИКАКОЙ return redirect('categories') И Т.Д.!!!
        return context

# Данный класс отвечает за отображение tinymce (GET запрос) и принятие из формы в метод POST (POST запрос)
@method_decorator(login_required(), name='dispatch')
class ShowDocumentView(TemplateView):
    template_name = 'profile_user/tinymce.html'

    # Функция для сохранения данных формы DocumentInfoForm
    def form_valid(self, document_info):
        # Как всегда веселая остановка сохранения для аккуратного сохранения того, что не указано
        save_document = document_info.save(commit=False)
        # Запись ссылки на хозяина
        save_document.user = self.request.user
        # Сохранение всего остального
        save_document.name = "Квитанция о приеме"
        save_document.save()
                
        return redirect("tiny_mce")

    def post(self, *args, **kwargs):
        
        # ЛИШНИМ НЕ БУДЕТ!
        # import bleach

        # sanitizer = bleach.Sanitizer()
        # cleaned_body = sanitizer.sanitize(form.cleaned_data['body'])
        # post.body = cleaned_body

        # Короче, почему стоит именно писать document_info = DocumentInfoForm(self.request.POST) вместо
        # document_info = self.request.POST.get('context')? ПОТОМУ что все изначально зависит от того, на
        # сколько у нас тесная связь между Frontend и Backend! Если она представляет из себя обычные взаимо-
        # действия (Получи и сохрани), то обязательно применять именно document_info = DocumentInfoForm(self.request.POST), 
        # потому-что основываясь на внесении в переменную форму с полученными данными, я смогу написать потом 
        # if document_info.is_valid(): , а вот если бы я писал document_info = self.request.POST.get('context'), то
        # джанго-функция к такому методу ПОЛУЧЕНИЯ информации - НЕ ПРИМЕНИМА! Да и еще это удобнее!
        # НЕ ЗАБЫВАЮ ПРО document_info.save(commit=False), save_document.name = "Квитанция о приеме", save_document.save() !
        document_info = DocumentInfoForm(self.request.POST) # Делать так нужно ОБЯЗАТЕЛЬНО!
        # Проверяю
        if document_info.is_valid():
            # Здесь активируется функция, которая отвечает за главное сохранение
            return self.form_valid(document_info)
        
        formset = DocumentInfoForm(self.request.POST)
        return self.render_to_response({'tiny_mce': formset})

    # Передаю в сайт методом GET форму самого tinymce
    def get(self, *args, **kwargs):
        formset = DocumentInfoForm()
        return self.render_to_response({'tiny_mce' : formset})
