"""Формы аккаунта: регистрация (поверх формы allauth) и настройки профиля."""
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.utils import timezone

from .models import User


class SignupForm(AllauthSignupForm):
    """Регистрация: имя, фамилия, email, пароль и согласие на обработку данных.

    Имя и фамилию allauth сам записывает в пользователя (adapter.save_user
    берёт first_name и last_name из cleaned_data).
    """

    first_name = forms.CharField(
        label='Имя', max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        label='Фамилия', max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )
    # Подпись со ссылками на документы — в шаблоне account/_consent_label.html
    privacy_consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        error_messages={'required': 'Без согласия зарегистрироваться нельзя.'},
    )

    field_order = ['first_name', 'last_name', 'email', 'password1', 'privacy_consent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # подписи и подсказки — как в макете, а не стандартные allauth
        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs['placeholder'] = 'you@example.com'
        self.fields['password1'].widget.attrs.pop('placeholder', None)

    def custom_signup(self, request, user):
        """Запоминаем, когда дано согласие (вызывается после создания пользователя)."""
        user.privacy_consent_at = timezone.now()
        user.save(update_fields=['privacy_consent_at'])


class ProfileForm(forms.ModelForm):
    """Настройки профиля: имя и фамилия (email меняется отдельно, с подтверждением)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {'first_name': 'Имя', 'last_name': 'Фамилия'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # в модели (AbstractUser) поля необязательные, на сайте — обязательные
        for field in self.fields.values():
            field.required = True
