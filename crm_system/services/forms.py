from django import forms
from django.contrib.auth import get_user_model
from services.models import ServicesInfo, CategoryServicesInfo
from tinymce.widgets import TinyMCE
from decimal import Decimal

User = get_user_model()

class ServicesWorkForm(forms.ModelForm):
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'min' : '0', 'autocomplete': 'off', 'class': 'no-spinners', 'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"}), label = 'Сумма, ₽')
    
    category = forms.CharField(
        label="Категория",
        widget=forms.Select(attrs={'class': 'select2-creatable'})
    )

    class Meta:
        model=ServicesInfo
        fields = ['name_service_work', 'price', 'category']
        labels = {"name_service_work": "Название услуги"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        categories = CategoryServicesInfo.objects.filter(user=self.user)
        choices = [('', '---------')] + [(c.name_category_work, c.name_category_work) for c in categories]
        self.fields['category'].widget.choices = choices

    def clean_price(self):
        value = self.cleaned_data.get('price')
        if value:
            clean_val = str(value).replace(" ", "").replace("\xa0", "").replace("\u202f", "")
            try:
                return Decimal(clean_val) 
            except Exception:
                raise forms.ValidationError("Введите корректное число.")
        return value

    def clean_name_service_work(self):
        name_service_work = self.cleaned_data.get('name_service_work').strip()
        return name_service_work
    
    def clean_category(self):
        category_value = self.cleaned_data.get('category')
        if not category_value:
            raise forms.ValidationError('Выберите или введите категорию')

        category_new_obj, created = CategoryServicesInfo.objects.get_or_create(name_category_work = category_value.strip(), user = self.user)
        return category_new_obj