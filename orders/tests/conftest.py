import pytest
from django.contrib.auth.models import User
from products.models import Product, Category, Brand
from basket.models import Basket, BasketItem
from orders.models import Order, OrderItem
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
def brand():
    """Фікстура для створення бренду"""
    return Brand.objects.create(
        name="Тестовий бренд",
        slug="test-brand"
    )


@pytest.fixture
def product(category, brand):
    """Фікстура для створення продукту"""
    return Product.objects.create(
        category=category,
        brand=brand,
        name="Тестовий продукт",
        slug="test-product",
        price=Decimal("1000.00"),
        available=True
    )


@pytest.fixture
def basket(user):
    """Фікстура для створення кошика"""
    return Basket.objects.create(user=user)


@pytest.fixture
def basket_item(basket, product):
    """Фікстура для створення товару в кошику"""
    return BasketItem.objects.create(
        basket=basket,
        product=product,
        quantity=2
    )


@pytest.fixture
def order(user):
    """Фікстура для створення замовлення"""
    return Order.objects.create(
        user=user,
        address="Київ, вул. Тестова, 1",
        address_ref="test_ref_123",
        status="pending"
    )


@pytest.fixture
def order_item(order, product):
    """Фікстура для створення товару в замовленні"""
    return OrderItem.objects.create(
        order=order,
        product=product,
        price=Decimal("1000.00"),
        quantity=1
    )