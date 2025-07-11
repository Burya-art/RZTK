from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from basket.models import BasketItem
from orders.models import Order
from reviews.models import Review
from django.core.exceptions import ValidationError
import re


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Електронна пошта", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': "Ім'я користувача",
            'password1': 'Пароль',
            'password2': 'Підтвердження пароля',
        }
        error_messages = {
            'password_mismatch': 'Паролі не збігаються.',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) > 20:
            raise ValidationError('Ім\'я користувача не може перевищувати 20 символів.')
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('Ім\'я користувача може містити лише літери, цифри та символи @/./+/-/_ .')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Це ім\'я користувача вже зайняте.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ця електронна пошта вже зареєстрована.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Паролі не збігаються.')
        return password2


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control form-control-sm'
            }),
        }


class OrderForm(forms.ModelForm):
    city = forms.CharField(label='Місто доставки', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введіть місто',
        'id': 'nova-poshta-city'
    }))
    address = forms.CharField(label='Відділення Нової Пошти', required=True)  # Меняем ChoiceField на CharField
    address_ref = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Order
        fields = ['city', 'address', 'address_ref']
        labels = {
            'address': 'Відділення доставки',
        }

    def clean_address(self):
        address = self.cleaned_data['address']
        if not address:
            raise forms.ValidationError("Будь ласка, оберіть відділення Нової Пошти.")
        return address


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваш коментар'}),
        }
