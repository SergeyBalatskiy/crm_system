from django import forms
from .models import ServiceInfo, WorkersInfo
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from .models import WorkersInfo, StatusCategory, DocumentInformation
from tinymce.widgets import TinyMCE

User = get_user_model()

class ServiceInfoForm(forms.ModelForm):
    """Форма для введения данных сервиса"""
    name_service = forms.CharField(label=None, widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Название сервиса'}))
    address = forms.CharField(label=None, widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Адрес'}))

    class Meta:
        model = ServiceInfo
        fields = ('name_service', 'address')

        labels = {'name_service' : '',
                  'address' : '',
                  }

    def name_service(self):
        name_service = self.cleaned_data.get('name_service').strip()
        return name_service

    def address(self):
        address = self.cleaned_data.get('address').strip()
        return address
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

# Переменная которая содержит в себе форму и добавление ее динамически
WorkersFormSet = modelformset_factory(
    WorkersInfo, fields=("name", "surname", "patronymic"), extra=1)

# Переменная которая содержит в себе форму для добавления категорий 
StatusesFormSet = modelformset_factory(
    StatusCategory, fields=("name", "color", "category"), extra=1)


class DocumentInfoForm(forms.ModelForm):
    """Форма для получения данных документа"""
    # Указываю, что форма будет браться на базе DocumentInformation
    class Meta:
        model = DocumentInformation
        # Мы говорим, что поле content будет основываться на базе HTMLField() из models
        fields = ('content',)  
        widgets = {'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),}
        labels = {'content': '', }