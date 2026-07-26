from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib import messages
from profile_user.models import StatusCategory, DocumentInformation, FormsForOrder
import csv
from django.contrib.staticfiles import finders
from django.conf import settings
from pathlib import Path

# Create your views here.
# Креате вью отвечает за создание нового обьекта на в связке с формой
class RegisterView(CreateView):
    # Само взаимодействие с формой
    form_class = CustomUserCreationForm
    # Какую страницу отображать (это просто с чем мы взаимодействуем)
    template_name = 'auth_registration/auth.html'
    # Что делать в случае 
    success_url = '/profile'

    # Диспатч является функцией аля-Бефор-рекуест
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    # Сохранение дефолтных категорий для заказов (статусов)
    def create_default_categories(self, user):
        default_categories = [
            {"name": "Новый", "color": "#3498db", "category":"new"},
            {"name": "На ремонте", "color": "#ac03f4", "category":"in_process"},
            {"name": "На согласовании", "color": "#ff8c00", "category":"deferred"},
            {"name": "Готов", "color": "#2ecc71", "category":"success"},
            {"name": "Отказ", "color": "#e74c3c", "category":"finished"},
            {"name": "Выдан", "color": "#666666", "category":"finished"},
        ]
        
        for element in default_categories:
            create_category = StatusCategory.objects.create(name=element["name"], color=element["color"], category=element["category"], user=user)
        
        # Возвращаю "ничего" потому что могу себе позволить!
        return None
    
    # Вызываю функцию которая отвечает за создание 4 дефолтных документов при регистрации
    def create_default_documents(self, user):

        # Создаю 2 списка, каждый будет связан с другим по названию и названию документа (для zip(documents, names))
        documents = ['addoption.txt', 'cancell.txt', 'complete.txt', 'garanty.txt']
        names = ['Акт о принятии', 'Акт о отказе', 'Акт о выполненных работах',  'Акт о гарантии']
        docs_waiting_to_create = []

        # Указываю путь до самого проекта
        # Короче, лучше уж использовать такую тактику с путями, как:
        # BASE_DIR = Path(__file__).resolve().parent.parent    + 
        # flie_path = BASE_DIR / 'auth_registration' / 'static' / 'auth_registration' / 'txt' / document
        # потому что это самый доступный способ для меня
        BASE_DIR = Path(__file__).resolve().parent.parent

        # Беру документ.txt и связанное с ним название
        for document, name in zip(documents, names):          

            # Указываю путь к каждому из 4 документов
            flie_path = BASE_DIR / 'auth_registration' / 'static' / 'auth_registration' / 'txt' / document

            # Открываю каждый файл отдельно, читаю что там, упаковываю в переменную
            with open(flie_path, 'r', encoding='utf-8') as file:
                write_content = file.read()
                
                # Здесь достаточно забавная механика, о которой я раньше не слышал, не знал, и при этом
                # эта механика весьма удобна и проста! можно не создавать отлельных N запроса, а всего лишь
                # создать словарь docs_waiting_to_create = [], потом добавлять туда каждый раз ссылку на саму БД с
                # аргументами на то что записывается внутри, и потом используя ссылку на саму БД.objects.bulk_create(docs_waiting_to_create)
                # можно таким образом за 1 действие записать 4 обьекта! Ну разве не сказка, а?
                docs_waiting_to_create.append(DocumentInformation(name=name, content=write_content, user=user))
        
        DocumentInformation.objects.bulk_create(docs_waiting_to_create)
        return None

    # Вызываю функцию которая отвечает за создание 2 дефолт форм отдельных для заказов
    def create_default_forms(self, user):
        types_of_orders = ['paid', 'warranty']
        forms_order_waiting = []

        for type_order in types_of_orders:
            forms_order_waiting.append(FormsForOrder(type_of_order = type_order, user = user))
        
        FormsForOrder.objects.bulk_create(forms_order_waiting)
        return None
    
    # Непосредственно отвечает за валидацию и принятие формы и ее сохранение
    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email  
        user.save() 

        # После сохранения я вызываю функцию которая задает дефолт статусы заказов
        self.create_default_categories(user)

        # После сохранения статусов заказов я вызываю функцию которая задает дефолт документы
        self.create_default_documents(user)

        # После сохранения 4 документов я вызываю функцию которая делает мне дефолт 
        # форму для заполнения информациизаказов
        self.create_default_forms(user)

        login(self.request, user)

        return redirect('profile')
    
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth_registration/auth.html'
    
    # Очень важное уточнение ЗДЕСЬ! ТАК как я использую LoginView, то
    # важно его писать именно обращаясь к классу с унаследованием функции супер
    # form_valid! Так как если этого не делать, то из за того, что ты напишешь так:
    #
    #    def form_valid(self, form):
    #    return redirect('profile')
    #
    # Получится так, что ты в текущей функции ПЕРЕЗАПИШЕШЬ ВСЮ ТУ МЕХАНИКУ, КОТОРАЯ
    # ПО дефолту реализована была уже!

    def form_valid(self, form):
        # Обязательно сначала "наследуюсь от супер функции form_valid"
        super().form_valid(form)
        return redirect('profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        return self.render_to_response({'login_form':form, 'registration_form': CustomUserCreationForm()})

# Темплейт вью отвечает за отображение всех элементов на сайте
class ShowForm(TemplateView):
    # Гоыворим, где нам применять темплейт вью
    template_name = 'auth_registration/auth.html'

    def dispatch(self, request, *args, **kwargs):
        # Тут редирект в случае того что пользователь авторизирован
        if request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)
    
    # Функция которая отвечает за отображение даннных в самом шаблоне сайта .html
    def get_context_data(self, **kwargs):
        # Это обязательно!!!
        context = super().get_context_data(**kwargs)
        # Передаем формы как регистрации так и логирования
        context['registration_form'] = CustomUserCreationForm()
        context['login_form'] = LoginForm()
        # Обязательно передается в виде словаря
        return context
    
