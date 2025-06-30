import pytest
from decimal import Decimal
from products.models import Brand, Category, Product


class TestSimpleValidation:
    @pytest.mark.django_db
    def test_available_products_filter(self, category):
        """Фільтрація тільки доступних продуктів"""
        Product.objects.create(
            category=category, name="Доступний",
            slug="available", price=Decimal("100"), available=True
        )
        Product.objects.create(
            category=category, name="Недоступний",
            slug="unavailable", price=Decimal("200"), available=False
        )

        available_count = Product.objects.filter(available=True).count()
        assert available_count == 1
    
    @pytest.mark.django_db
    def test_product_str_method(self, product):
        """Перевіряємо що __str__ повертає назву продукту"""
        assert str(product) == "MacBook Pro 14"
        assert str(product) == product.name
    
    def test_model_table_names(self):
        """Перевіряємо що назви таблиць відповідають назвам моделей"""
        assert Product._meta.db_table == 'products'
        assert Category._meta.db_table == 'categories'
        assert Brand._meta.db_table == 'brands'
