from django import forms

from orders.models import CreateServiceWork


class ServiceInfoForm(forms.ModelForm):
    """Форма для введения данных для создания истории на ремонт"""

    class Meta:
        model = CreateServiceWork
        fields = ('service_provided', 'service_price', 'quantity_was_used', 'detail_name_was_used')

        labels = {'service_provided' : 'Название услуги',
                  'service_price' : 'Цена услуги',
                  'quantity_was_used' : 'Количество (в используемых в деталях)',
                  'detail_name_was_used' : 'Название используемой детали',
                  }

    def service_provided(self):
        service_provided = self.cleaned_data.get('service_provided').strip()
        return service_provided

    def quantity_was_used(self):
        quantity_was_used = self.cleaned_data.get('quantity_was_used').strip()
        return quantity_was_used