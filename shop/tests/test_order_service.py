import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from shop.models import Product, Category, Basket, BasketItem, Order, OrderItem
from shop.services.order import create_order_from_basket
from unittest.mock import patch
from django.shortcuts import get_object_or_404


@pytest.mark.django_db
class TestOrderService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price=100.00,
            available=True
        )
        self.basket = Basket.objects.create(user=self.user)
        self.basket_item = BasketItem.objects.create(
            basket=self.basket,
            product=self.product,
            quantity=2
        )

    def test_create_order_from_basket_success(self):
        """Тестує успішне створення замовлення."""
        order = create_order_from_basket(
            user=self.user,
            city='Kyiv',
            address='Nova Poshta #1',
            address_ref='ref123'
        )
        assert Order.objects.count() == 1
        assert OrderItem.objects.count() == 1
        assert BasketItem.objects.count() == 0  # Кошик очищено
        assert order.user == self.user
        assert order.address == 'Kyiv, Nova Poshta #1'
        assert order.address_ref == 'ref123'
        order_item = OrderItem.objects.first()
        assert order_item.product == self.product
        assert order_item.quantity == 2
        assert order_item.price == 100.00

    def test_create_order_from_basket_empty_basket(self):
        """Тестує створення замовлення з порожнім кошиком."""
        BasketItem.objects.all().delete()  # Очищаємо кошик
        with pytest.raises(ValueError, match="Кошик порожній. Додайте товари перед оформленням замовлення."):
            create_order_from_basket(self.user, 'Kyiv', 'Nova Poshta #1', 'ref123')

    @patch('shop.services.order.get_object_or_404')
    def test_create_order_from_basket_no_basket(self, mock_get_object_or_404):
        """Тестує випадок, коли кошик не існує."""
        mock_get_object_or_404.side_effect = Exception('Basket not found')
        with pytest.raises(Exception, match='Basket not found'):
            create_order_from_basket(self.user, 'Kyiv', 'Nova Poshta #1', 'ref123')
