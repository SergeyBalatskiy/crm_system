from django import forms
from orders.models import CreateServiceWork
from django.core.exceptions import ValidationError
from dal_select2.widgets import Select2

class WorkCreatingForm(forms.ModelForm):
    """Форма для введения данных для создания истории на ремонт"""

    class Meta:
        model = CreateServiceWork
        fields = ('service_provided', 'quantity_was_used', 'days_of_garanty', 'service_price', 'detail_name_was_used', 'detail_id')

        labels = {'service_provided' : 'Наименование',
                  'quantity_was_used' : 'Кол-во',
                  'days_of_garanty' : 'Гарантия, дней',
                  'service_price' : 'Цена, руб',
                  'detail_name_was_used' : 'Название товара',
                  'detail_id' : 'Код товара'
                  }

        widgets = {
            'detail_name_was_used': Select2(url='orders_autocomplete', attrs = {
                'data-placeholder' : 'Выберите деталь, используемую при работе...',
                'style' : 'width: 100%;',
                }), 

            # Эти поля заблокированы от ручного ввода 
            'detail_id': forms.TextInput(attrs={'class': 'form-control readonly-input', 'readonly': 'readonly'}),
            
            # Заменено на TextInput для корректной работы форматирования пробелов в JS
            # Название услуги можно ввести вручную, либо же выбрать
            'service_provided' : Select2(url='services_autocomplete', attrs = {
                'data-placeholder' : 'Выберите или введите услугу...',
                'data-tags' : 'true', 'style' : 'width: 100%;',
            }), 
            'days_of_garanty': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'placeholder': 'Гарантия'}),
            'service_price': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'placeholder': 'Цена услуги'}),
            'quantity_was_used': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'placeholder': 'Количество'}),
        }

    # Идет проверка на корректность ввода (чтобы не было пустым) + очистка:
    def clean_service_provided(self):
        service_provided = self.cleaned_data.get('service_provided').strip()
        if not service_provided:
            raise ValidationError('Необходимо указать название оказываемой услуги!')
        return service_provided

    # Идет проверка на корректность ввода (чтобы не было пустым) + очистка:
    def clean_service_price(self):
        service_price = self.cleaned_data.get('service_price')
        if not service_price:
            raise ValidationError('Необходимо указать цену оказываемой услуги!')
        return service_price

    def clean(self):
        cleaned_data=super().clean()
        name_selected_product = cleaned_data.get('detail_name_was_used')
        quantity_was_used = cleaned_data.get('quantity_was_used')

        if quantity_was_used and not name_selected_product:
            self.add_error('quantity_was_used', 'Нельзя списать товар, который не выбран!')

        if name_selected_product and not quantity_was_used:
            self.add_error('detail_name_was_used', 'Необходимо указать количество используемого товара!')

        return cleaned_data
       