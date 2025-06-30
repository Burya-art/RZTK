import pytest
from django.contrib.auth.models import User
from products.models import Product, Category, Brand
from reviews.models import Review
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
def review(user, product):
    """Фікстура для створення відгуку"""
    return Review.objects.create(
        product=product,
        user=user,
        comment="Дуже хороший продукт!"
    )