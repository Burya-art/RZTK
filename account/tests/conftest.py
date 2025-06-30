import pytest
from django.contrib.auth.models import User
from django.test import Client
from products.models import Product, Category
from orders.models import Order
from decimal import Decimal


@pytest.fixture
def user():
    """Фікстура для створення користувача"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def authenticated_client(user):
    """Фікстура для автентифікованого клієнта"""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def category():
    """Фікстура для створення категорії"""
    return Category.objects.create(
        name="Тестова категорія",
        slug="test-category"
    )


@pytest.fixture
def product(category):
    """Фікстура для створення продукту"""
    return Product.objects.create(
        category=category,
        name="Тестовий продукт",
        slug="test-product",
        price=Decimal("1000.00"),
        available=True
    )


@pytest.fixture
def order(user):
    """Фікстура для створення замовлення"""
    return Order.objects.create(
        user=user,
        address="Тестова адреса, Київ",
        status="pending"
    )