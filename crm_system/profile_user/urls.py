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
    # Указываю на путь к редактированию форм для заказа
    path('form-editor', FormsForOrdersEdit.as_view(), name='form-editor'),
    # Указываю на путь, где лежит центральное окно с возможностью корректировки каждой формы индивидуально
    path('edit-individual-form', EditIndividualCenterForm.as_view(), name='get-individual-field-modal'),
    
]
