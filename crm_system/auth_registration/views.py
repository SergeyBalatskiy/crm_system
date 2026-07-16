from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib import messages
from profile_user.models import StatusCategory, DocumentInformation

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

        default_categories = [
            {"name": "Акт о выдаче", "content": "Акт о выдаче тут типо написан"},
            {"name": "Акт о принятии", "content": "Акт о принятии типо тут написан"},
            {"name": "Акт о отказе", "content": "Акт о отказе тут написан"},
            {"name": "Акт о выполненных работах", "content": "Акт о выполненных работах тут написан"}

        ]
        for element in default_categories:
            create_document = DocumentInformation.objects.create(name=element["name"], content=element["content"], user=user)
        return None

    # Непосредственно отвечает за валидацию и принятие формы и ее сохранение
    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email  
        user.save() 
        print('Сохранил:', user.username)
        print('Сохранил:', user.email)
        # После сохранения я вызываю функцию которая задает дефолт статусы заказов
        self.create_default_categories(user)
        # После сохранения статусов заказов я вызываю функцию которая задает дефолт документы
        self.create_default_documents(user)
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
    
