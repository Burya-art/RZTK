import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestAuthentication:
    """Прості тести для автентифікації"""
    
    @pytest.mark.django_db
    def test_user_creation(self):
        """Тест створення користувача"""
        user = User.objects.create_user(
            username="testuser", 
            email="test@example.com",
            password="testpass123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
    
    @pytest.mark.django_db  
    def test_login_view_get(self):
        """Тест GET запиту до сторінки логіну"""
        client = Client()
        url = reverse('account:login')
        response = client.get(url)
        
        assert response.status_code == 200
    
    @pytest.mark.django_db
    def test_login_view_post_valid(self, user):
        """Тест успішного логіну"""
        client = Client()
        url = reverse('account:login')
        
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = client.post(url, form_data)
        
        # Перевіряємо що користувач увійшов
        assert response.status_code == 302
        
        # Перевіряємо що сесія містить користувача
        assert '_auth_user_id' in client.session
    
    @pytest.mark.django_db
    def test_logout_redirect(self, authenticated_client):
        """Тест що logout перенаправляє на список продуктів"""
        url = reverse('account:logout')
        response = authenticated_client.post(url)
        
        assert response.status_code == 302
        # Перевіряємо редірект на products:product_list
        assert response.url == reverse('products:product_list')
    
    @pytest.mark.django_db
    def test_user_str_method(self, user):
        """Тест методу __str__ користувача"""
        assert str(user) == "testuser"
