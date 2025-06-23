import pytest
from django.contrib.auth.models import User
from shop.models import Basket, BasketItem, Product, Category
from shop.services.basket import BasketService


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def category():
    return Category.objects.create(name='Test Category', slug='test-category')


@pytest.fixture
def product(category):
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        price=100.00,
        available=True
    )


@pytest.fixture
def product2(category):
    return Product.objects.create(
        name='Test Product 2',
        slug='test-product-2',
        category=category,
        price=200.00,
        available=True
    )


@pytest.mark.django_db
class TestBasketService:
    """Тести для BasketService"""

    def test_get_or_create_basket_new_user(self, user):
        """Тест створення нової корзини для користувача"""
        basket = BasketService.get_or_create_basket(user)
        
        assert basket.user == user
        assert Basket.objects.filter(user=user).count() == 1

    def test_get_or_create_basket_existing_user(self, user):
        """Тест отримання існуючої корзини"""
        # Створюємо корзину
        existing_basket = Basket.objects.create(user=user)
        
        # Отримуємо корзину через сервіс
        basket = BasketService.get_or_create_basket(user)
        
        assert basket.id == existing_basket.id
        assert Basket.objects.filter(user=user).count() == 1

    def test_add_product_to_basket_new_product(self, user, product):
        """Тест додавання нового товару до корзини"""
        basket_item = BasketService.add_product_to_basket(user, product.id, 2)
        
        assert basket_item.product == product
        assert basket_item.quantity == 2
        assert basket_item.basket.user == user

    def test_add_product_to_basket_existing_product(self, user, product):
        """Тест додавання існуючого товару до корзини"""
        # Додаємо товар вперше
        BasketService.add_product_to_basket(user, product.id, 2)
        
        # Додаємо той самий товар ще раз
        basket_item = BasketService.add_product_to_basket(user, product.id, 3)
        
        assert basket_item.quantity == 5  # 2 + 3
        assert BasketItem.objects.filter(product=product).count() == 1

    def test_update_basket_item_quantity(self, user, product):
        """Тест оновлення кількості товару в корзині"""
        # Додаємо товар
        basket_item = BasketService.add_product_to_basket(user, product.id, 2)
        
        # Оновлюємо кількість
        updated_item = BasketService.update_basket_item_quantity(user, basket_item.id, 5)
        
        assert updated_item.quantity == 5
        assert updated_item.id == basket_item.id

    def test_remove_item_from_basket(self, user, product):
        """Тест видалення товару з корзини"""
        # Додаємо товар
        basket_item = BasketService.add_product_to_basket(user, product.id, 2)
        item_id = basket_item.id
        
        # Видаляємо товар
        BasketService.remove_item_from_basket(user, item_id)
        
        assert not BasketItem.objects.filter(id=item_id).exists()

    def test_clear_basket(self, user, product, product2):
        """Тест очищення корзини"""
        # Додаємо кілька товарів
        BasketService.add_product_to_basket(user, product.id, 2)
        BasketService.add_product_to_basket(user, product2.id, 1)
        
        basket = BasketService.get_or_create_basket(user)
        assert basket.items.count() == 2
        
        # Очищуємо корзину
        BasketService.clear_basket(user)
        
        basket.refresh_from_db()
        assert basket.items.count() == 0

    def test_get_basket_total_price(self, user, product, product2):
        """Тест розрахунку загальної вартості корзини"""
        # Додаємо товари
        BasketService.add_product_to_basket(user, product.id, 2)    # 2 * 100 = 200
        BasketService.add_product_to_basket(user, product2.id, 1)   # 1 * 200 = 200
        
        total_price = BasketService.get_basket_total_price(user)
        
        assert total_price == 400.00

    def test_get_basket_total_price_empty_basket(self, user):
        """Тест розрахунку вартості порожньої корзини"""
        total_price = BasketService.get_basket_total_price(user)
        
        assert total_price == 0.00

    def test_is_basket_empty_with_items(self, user, product):
        """Тест перевірки порожньої корзини з товарами"""
        BasketService.add_product_to_basket(user, product.id, 1)
        
        is_empty = BasketService.is_basket_empty(user)
        
        assert not is_empty

    def test_is_basket_empty_without_items(self, user):
        """Тест перевірки порожньої корзини без товарів"""
        is_empty = BasketService.is_basket_empty(user)
        
        assert is_empty

    def test_basket_service_with_different_users(self, product):
        """Тест роботи сервісу з різними користувачами"""
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')
        
        # Додаємо товари різним користувачам
        BasketService.add_product_to_basket(user1, product.id, 1)
        BasketService.add_product_to_basket(user2, product.id, 2)
        
        # Перевіряємо що корзини незалежні
        total1 = BasketService.get_basket_total_price(user1)
        total2 = BasketService.get_basket_total_price(user2)
        
        assert total1 == 100.00  # 1 * 100
        assert total2 == 200.00  # 2 * 100
        
        # Очищуємо корзину одного користувача
        BasketService.clear_basket(user1)
        
        assert BasketService.is_basket_empty(user1)
        assert not BasketService.is_basket_empty(user2)