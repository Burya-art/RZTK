import pytest
from decimal import Decimal
from products.models import Brand, Category, Product


@pytest.mark.django_db
class TestProductModels:
    """Тести для моделей продуктів"""
    
    def test_category_creation(self, category):
        """Тест створення категорії"""
        assert category.name == "Ноутбуки"
        assert category.slug == "notebooks"
        assert str(category) == "Ноутбуки"

    def test_brand_creation(self, brand):
        """Тест створення бренду"""
        assert brand.name == "Apple"
        assert brand.slug == "apple"
        assert str(brand) == "Apple"
    
    def test_product_creation(self, product):
        """Тест створення продукту"""
        assert product.name == "MacBook Pro 14"
        assert product.slug == "macbook-pro-14"
        assert product.price == Decimal("89999.99")
        assert product.available is True
        assert str(product) == "MacBook Pro 14"
    
    def test_product_relationships(self, product, category, brand):
        """Тест зв'язків між моделями"""
        assert product.category == category
        assert product.brand == brand
        assert product in category.products.all()
        assert product in brand.products.all()
