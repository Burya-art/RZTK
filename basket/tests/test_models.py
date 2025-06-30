import pytest
from basket.models import Basket, BasketItem
from decimal import Decimal


@pytest.mark.django_db
class TestBasketModel:
    def test_basket_creation(self, user):
        """Тест створення кошика"""
        basket = Basket.objects.create(user=user)

        assert basket.user == user
        assert basket.created is not None
        assert basket.updated is not None

    def test_basket_db_table(self):
        """Тест назви таблиці кошика"""
        assert Basket._meta.db_table == 'baskets'


@pytest.mark.django_db
class TestBasketItemModel:
    """Тести для моделі BasketItem"""

    def test_basket_item_creation(self, basket_item):
        """Тест створення товару в кошику"""
        assert basket_item.quantity == 2
        assert basket_item.product.name == "Тестовий продукт"
        assert basket_item.basket.user.username == "testuser"

    def test_basket_item_str_method(self, basket_item):
        """Тест методу __str__ товару в кошику"""
        expected = f'{basket_item.quantity} x {basket_item.product.name}'
        assert str(basket_item) == expected

    def test_basket_item_total_price(self, basket_item):
        """Тест розрахунку загальної ціни товару"""
        expected_price = basket_item.quantity * basket_item.product.price
        assert basket_item.get_total_price() == expected_price
        assert basket_item.get_total_price() == Decimal("2000.00")

    def test_basket_item_db_table(self):
        """Тест назви таблиці товарів в кошику"""
        assert BasketItem._meta.db_table == 'basket_items'

    def test_basket_item_default_quantity(self, basket, product):
        """Тест значення за замовчуванням для кількості"""
        item = BasketItem.objects.create(basket=basket, product=product)
        assert item.quantity == 1
