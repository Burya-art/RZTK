import pytest 111
from decimal import Decimal
from products.models import Brand, Category, Product


@pytest.fixture
def category():
    """Фікстура для створення категорії"""
    return Category.objects.create(
        name="Ноутбуки",
        slug="notebooks"
    )


@pytest.fixture
def brand():
    """Фікстура для створення бренду"""
    return Brand.objects.create(
        name="Apple",
        slug="apple"
    )


@pytest.fixture
def product(category, brand):
    """Фікстура для створення продукту"""
    return Product.objects.create(
        category=category,
        brand=brand,
        name="MacBook Pro 14",
        slug="macbook-pro-14",
        description="Потужний ноутбук для професіоналів",
        price=Decimal("89999.99"),
        available=True
    )