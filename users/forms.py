from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        required=True, 
        label='Имя', 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'})
        )
    email = forms.EmailField(required=True,
        label='email', 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'})
        )
    phone =  forms.CharField(
        required=True,
        max_length=32,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__'
        })
        )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )
    password2 = forms.CharField(
        label='Подтвердите пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        '''Сохраняем email в модель'''
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = User.Roles.CLIENT  
        if commit:
            user.save()
        return user
