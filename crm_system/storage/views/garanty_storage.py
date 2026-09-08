from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from storage.models import HistoryStorageInfo, StorageInfo
from django.shortcuts import render, redirect
from storage.forms import GarantyHistoryForm
from django.utils import timezone
from django.contrib import messages


# Данный класс отвечает за показ сайта, где можно изьять/удалить товары на складе (имеющиеся)
@method_decorator(login_required(), name='dispatch') 
class StorageGarantyCustomView(TemplateView):

    def post(self, request, *args, **kwargs):
    
            # Получаю все формсеты, которые есть
            formset = GarantyHistoryForm(request.POST)
    
            # Валидация форм (пропуск не важных полей) + сохранение важных
            if formset.is_valid():
    
                # Остановка сохранения 
                instances = formset.save(commit=False)

                # Беру каждый обьект из формсета и индивидуально в каждом записываю юзера и сохраняю
                for instance in instances:
                    history_data = StorageInfo.objects.filter(individual_code=instance.individual_code_history).first()
                    instance.user = request.user
                    instance.type_of_operation_history = "Гарантийный возврат"
                    instance.individual_code_history = history_data.individual_code
                    current_remainder_instance = instance.quantity_history
                    instance.remainder_history = history_data.remainder - current_remainder_instance
                    history_data.remainder = history_data.remainder - current_remainder_instance
                    instance.time_created_history = history_data.created_at
                    instance.time_of_operation_history = timezone.now()
                    instance.save()

                    # Обновляю обьект (один) в StorageInfo, чтобы его впоследствии и брать, и взаимодействовать.
                    history_data.save()
    
                messages.success(request, 'Товары были успешно списаны со склада, компенсация за товар была возвращена!')
                return redirect('history-storage')
    
            return redirect('removal-form-storage')
        