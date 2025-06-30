import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAccountViews:
    def test_register_view_get(self):
        """Тест GET запиту до сторінки реєстрації"""
        client = Client()
        url = reverse('account:register')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_register_view_post_valid(self):
        """Тест успішної реєстрації користувача"""
        client = Client()
        url = reverse('account:register')
        
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        
        response = client.post(url, form_data)
        
        # Перевіряємо що користувач створений
        assert User.objects.filter(username='newuser').exists()
        
        # Перевіряємо редірект після успішної реєстрації
        assert response.status_code == 302
    
    def test_profile_view_requires_login(self):
        """Тест що профіль потребує авторизації"""
        client = Client()
        url = reverse('account:profile')
        response = client.get(url)
        
        # Має перенаправити на логін
        assert response.status_code == 302
        assert '/account/login/' in response.url
    
    def test_profile_view_authenticated(self, authenticated_client, user, order):
        """Тест доступу до профілю для автентифікованого користувача"""
        url = reverse('account:profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.context['user'] == user
        assert 'orders' in response.context
