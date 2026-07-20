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
