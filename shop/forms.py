from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import BasketItem, Order, Review


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


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

















