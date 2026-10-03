from django import forms
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from services.models import ServicesInfo
from tinymce.widgets import TinyMCE

User = get_user_model()

class ServicesWorkForm(forms.ModelForm):
    """Форма для введения данных оказания услуг"""

    class Meta:
        model = ServicesInfo
        # Выбираю поля на показ
        fields = ['name_service_work', 'price', 'category']
        
        # Даю название этим полям (они будут находиться рядом с самим полем)
        labels = {'name_service_work' : 'Название оказанной услуги',
                  'price' : 'Цена',
                  'category' : 'Категория услуги'
                  }

    def name_service_work(self):
        name_service_work = self.cleaned_data.get('name_service_work').strip()
        return name_service_work

    def price(self):
        price = self.cleaned_data.get('price').strip()
        return price
    
    def category(self):
        category = self.cleaned_data.get('category').strip()
        return category
 