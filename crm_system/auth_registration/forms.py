from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm

# Здесь мы сохраняем в переменную ссылку на классовую модель
# текущего пользователя
User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    """Форма для регистрации пользователей"""
    first_name = forms.CharField(label=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(label=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    phone_number = forms.CharField(label=False, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефона'}))
    email = forms.EmailField(label=False, max_length=255, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'почта'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}))
    
    # Как правило класс мета задает настройки для формы
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'email')

    # Функции клин всегда как правило предоставляют предобработку перед сохранением
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2
    
    def clean_first_name(self):
        name = self.cleaned_data.get('first_name')
        # Проверка на пустоту
        if not name.strip():
            raise forms.ValidationError("Имя не может быть пустым!")
        # Проверка на наличие цифр
        if any(c.isdigit() for c in name):
            raise forms.ValidationError("Имя не должно содержать цифры!")
        # Очищаем, приводим в норм состояние
        formatted_name = name.strip().title()
        return formatted_name

    def clean_last_name(self):
        lst_name = self.cleaned_data.get('last_name')
        # Проверка на пустоту
        if not lst_name.strip():
            raise forms.ValidationError("Фамилия не может быть пустой!")
        # Проверка на наличие цифр
        if any(c.isdigit() for c in lst_name):
            raise forms.ValidationError("Фамилия не должна содержать цифры!")
        # Очищаем, приводим в норм состояние
        formatted_name = lst_name.strip().title()
        return formatted_name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        """
        Форматирует номер телефона в стандартный вид: +7 (XXX) XXX-XX-XX
        Принимает различные форматы ввода.
        """
        # Удаляем все нецифровые символы
        digits = ''.join(c for c in phone if c.isdigit())

        # Проверка длины номера
        if len(digits) < 10 or len(digits) > 11:
            raise forms.ValidationError("Некорректная длина номера!")

        # Обработка номера без кода страны
        if len(digits) == 10:
            digits = '7' + digits

        # Проверка кода страны
        if digits[0] not in ['7', '8']:
            raise forms.ValidationError("Номер должен начинаться с 7 или 8!")

        # Форматирование номера
        formatted_number = '+7 ({}) {}-{}-{}'.format(
        digits[1:4], digits[4:7], digits[7:9], digits[9:11]
        )

        return formatted_number

    # Функция сейв непосредственно соханяет данные из формы
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        raw_password = self.cleaned_data['password1']
        hashed_password = make_password(raw_password)
        user.password = hashed_password
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    """Форма для аутентификации пользователей"""
    username = forms.EmailField(label=False, max_length=255,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Почта'}))
    password = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
    