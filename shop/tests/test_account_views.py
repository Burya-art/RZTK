import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Order


@pytest.fixture
def client():
    """Фікстура для неавторизованого клієнта"""
    return Client()


@pytest.fixture
def user():
    """Фікстура для створення користувача"""
    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='TestPass123!'
    )


@pytest.fixture
def auth_client(client, user):
    """Фікстура для авторизованого клієнта"""
    client.login(username='testuser', password='TestPass123!')
    return client


@pytest.mark.django_db
class TestAccountViews:
    """Тести для облікового запису"""

    def test_register(self, client):
        """Тест реєстрації користувача"""
        response = client.post(reverse('account:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        })
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_profile(self, auth_client, user):
        """Тест сторінки профілю"""
        response = auth_client.get(reverse('account:profile'))
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_cancel_order(self, auth_client, user):
        """Тест скасування замовлення"""
        # Створюємо замовлення зі статусом pending
        order = Order.objects.create(
            user=user,
            address='Тестова адреса',
            status='pending'
        )

        response = auth_client.post(
            reverse('account:cancel_order', args=[order.id])
        )
        order.refresh_from_db()
        assert response.status_code == 302
        assert order.status == 'cancelled'
