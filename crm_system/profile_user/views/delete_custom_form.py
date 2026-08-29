from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from profile_user.models import FormsForOrder
from django.http import HttpResponse
import json

# Классовое представление удаления кастомной формы
@method_decorator(login_required(), name='dispatch')

class DeleteCustomForm(TemplateView):

    def post(self, request, *args, **kwargs):

        type_of_order_selected = request.POST.get('type_of_order_selected')

        objects_show = request.POST.get('objects_show')
        print("1111212", objects_show)

        # ["custom-1"]
        deleted_custom_forms = request.POST.get('deleted_custom_forms')

        deleted_custom_forms = json.loads(deleted_custom_forms)

        for object_custom_form in deleted_custom_forms:
            deleted_custom_forms = object_custom_form

        order_information = FormsForOrder.objects.filter(
                type_of_order=type_of_order_selected, 
                user=self.request.user
            ).first()
        
        json_models_data = order_information.json_forms

        for section in json_models_data.get('sections', []):
            if section.get('id') == objects_show:

                custom_forms = section.get('custom_forms')
                saved_hints = section.get('saved_hints')
                for selected_form in custom_forms:

                    if deleted_custom_forms in selected_form['field_key']:
                        custom_forms.remove(selected_form)
                        print(custom_forms)
                        print('Удалена форма')
                        break

                for hint_obj_to_delete in saved_hints:
                    if deleted_custom_forms in hint_obj_to_delete:
                        del saved_hints[hint_obj_to_delete]
                        print('Удален автоответ')
                        print(saved_hints)
                        break

                print("Сохранение в БД!")
                # Сохранение изменений в БД
                order_information.json_forms = json_models_data
                order_information.save()
                
                # Для GET запроса
                args_for_get_trigger = {
                    "formCreated": {
                    "objects_show": objects_show,
                    "type_of_order_selected": type_of_order_selected
                        }
                    }
                response = HttpResponse(status=204)
                response["HX-Trigger"] = json.dumps(args_for_get_trigger)
                return response




                        
    