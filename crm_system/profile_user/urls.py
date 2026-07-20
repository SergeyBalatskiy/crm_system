from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

# Веселые маршруты... как я на них навернулся...
urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    # Выход пользователя из авторизации
    path('logout', LogoutView.as_view(next_page="auth"), name='logout'),
    # Отображение сайта для настройки данных сервиса
    path('service_info', ServiceInfoView.as_view(), name = 'service_info'),
    # Отображение формы для ввода данных сотрудников
    path('workers_info', WorkersAddView.as_view(), name='workers_info'),
    # Показ категорий для заказов
    path('categories', ShowCategoriesView.as_view(), name='categories'),
    # Указываю на путь к редактированию документов
    path('documents', ShowDocumentView.as_view(), name='tiny_mce'),
    # Указываю путь к показу и редактированию именно АКТА О гарантии
    path('document1', ShowGarantyView.as_view(), name = 'garanty_doc'),
    # Указываю путь к показу и редактированию именно АКТА О ПРИНЯТИИ
    path('document2', ShowAdoptionView.as_view(), name = 'adoption_doc'),
    # Указываю путь к показу и редактированию именно АКТА О ОТКАЗЕ
    path('document3', ShowCancellView.as_view(), name = 'cancell_doc'),
    # Указываю путь к показу и редактированию именно АКТ О ВЫПОЛНЕННЫХ РАБОТАХ
    path('document4', ShowCompleteView.as_view(), name = 'complete_doc'),
]
