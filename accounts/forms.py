from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "address", "avatar"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Электронная почта",
        widget=forms.EmailInput(attrs={
            "class": "form-control", 
            "placeholder": "Ваш email",
            "autocomplete": "email"
        })
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        labels = {
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Безопасно скрываем username если он есть в форме
        if 'username' in self.fields:
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].required = False
        
        # Переводим help_text паролей
        self.fields['password1'].help_text = """
        <small class="help-text">
        • Пароль не должен быть слишком похож на другую вашу личную информацию.<br>
        • Пароль должен содержать как минимум 8 символов.<br>
        • Пароль не должен быть слишком простым и распространенным.<br>
        • Пароль не может состоять только из цифр.
        </small>
        """
        
        self.fields['password2'].help_text = """
        <small class="help-text">
        Для подтверждения введите, пожалуйста, пароль ещё раз.
        </small>
        """

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        # Автоматически создаем username из email
        if email:
            cleaned_data['username'] = email
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # используем email как username
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user