import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from shop.models import Basket, BasketItem, Product, Category, Order, OrderItem
from shop.forms import OrderForm


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def auth_client(user):
    """Фікстура для авторизованого клієнта"""
    client = Client()
    client.login(username='testuser', password='12345')
    return client


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
def basket(user):
    return Basket.objects.create(user=user)


@pytest.fixture
def basket_item(basket, product):
    return BasketItem.objects.create(basket=basket, product=product, quantity=2)


@pytest.mark.django_db
def test_create_order_success(user, basket, basket_item):
    client = Client()
    client.login(username='testuser', password='12345')
    url = reverse('shop:create_order')
    data = {'city': 'Kyiv', 'address': 'Nova Poshta #1', 'address_ref': 'ref123'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('shop:product_list')
    assert Order.objects.count() == 1
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any(f'Замовлення #{Order.objects.first().id} успішно створено!' in msg for msg in messages)


@pytest.mark.django_db
def test_create_order_empty_basket(user, basket):
    client = Client()
    client.login(username='testuser', password='12345')
    BasketItem.objects.all().delete()
    url = reverse('shop:create_order')
    data = {'city': 'Kyiv', 'address': 'Nova Poshta #1', 'address_ref': 'ref123'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('shop:basket_detail')
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert 'Кошик порожній. Додайте товари перед оформленням замовлення.' in messages
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_invalid_form(user, basket, basket_item):
    client = Client()
    client.login(username='testuser', password='12345')
    url = reverse('shop:create_order')
    data = {'city': '', 'address': '', 'address_ref': ''}  # Невалідні дані
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('shop:basket_detail')
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any("Помилка в полі" in msg for msg in messages)
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_non_post_request(user):
    client = Client()
    client.login(username='testuser', password='12345')
    url = reverse('shop:create_order')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('shop:basket_detail')
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_unauthenticated():
    client = Client()
    url = reverse('shop:create_order')
    data = {'city': 'Kyiv', 'address': 'Nova Poshta #1', 'address_ref': 'ref123'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert 'login' in response.url
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_create_order_from_basket_service(user, basket, basket_item):
    """Тест безпосередньо функції create_order_from_basket"""
    from shop.services.order import create_order_from_basket

    order = create_order_from_basket(
        user=user,
        city='Київ',
        address='Відділення №1',
        address_ref='ref123'
    )

    assert order.user == user
    assert order.address == 'Київ, Відділення №1'
    assert order.items.count() == 1
    assert basket.items.count() == 0  # Кошик очищено


@pytest.mark.django_db
def test_create_order_large_quantity(user, basket, basket_item):
    """Тест з великою кількістю одного товару"""
    # Оновлюємо кількість у існуючому basket_item
    large_quantity = 999
    basket_item.quantity = large_quantity
    basket_item.save()

    client = Client()
    client.login(username='testuser', password='12345')

    url = reverse('shop:create_order')
    data = {
        'city': 'Київ',
        'address': 'Відділення №1',
        'address_ref': 'ref123'
    }
    response = client.post(url, data)

    # Перевіряємо створення замовлення
    assert response.status_code == 302
    order = Order.objects.first()
    order_item = order.items.first()

    # Перевіряємо кількість та суму
    assert order_item.quantity == large_quantity
    expected_total = basket_item.product.price * large_quantity
    assert order.get_total_price() == expected_total

    # Перевіряємо очищення кошика
    assert basket.items.count() == 0


@pytest.mark.django_db
def test_create_order_multiple_items(auth_client, user, basket, product, category):
    """Тест створення замовлення з кількома різними товарами"""
    # Додаємо другий товар
    product2 = Product.objects.create(
        name='Ноутбук ASUS',
        slug='notebook-asus',
        category=category,
        price=25000.00
    )

    # Наповнюємо кошик
    BasketItem.objects.create(basket=basket, product=product, quantity=3)
    BasketItem.objects.create(basket=basket, product=product2, quantity=1)

    # Створюємо замовлення (використовуємо auth_client замість client)
    response = auth_client.post(reverse('shop:create_order'), {
        'city': 'Київ',
        'address': 'Відділення №15',
        'address_ref': 'ref123'
    })

    # Перевірки
    # Базові перевірки
    assert response.status_code == 302
    assert response.url == reverse('shop:product_list')  # Куди редирект

    # Перевірка створення замовлення
    assert Order.objects.count() == 1  # Лише одне замовлення створено
    order = Order.objects.first()
    assert order.user == user  # Правильний користувач
    assert order.items.count() == 2

    # Детальна перевірка товарів у замовленні
    order_item1 = order.items.get(product=product)
    assert order_item1.quantity == 3
    assert order_item1.price == product.price  # Ціна зафіксована на момент замовлення

    order_item2 = order.items.get(product=product2)
    assert order_item2.quantity == 1
    assert order_item2.price == product2.price

    # Перевірка розрахунків
    assert order_item1.get_total_price() == 300  # 3 * 100
    assert order_item2.get_total_price() == 25000  # 1 * 25000
    assert order.get_total_price() == 25300

    # Перевірка адреси доставки
    assert order.address == 'Київ, Відділення №15'
    assert order.address_ref == 'ref123'
    assert order.status == 'pending'  # Початковий статус


@pytest.mark.django_db
def test_cascade_delete_user_orders(user, basket, basket_item):
    """Тест каскадного видалення замовлень при видаленні користувача"""
    from shop.services.order import create_order_from_basket

    # Створюємо замовлення
    order = create_order_from_basket(
        user=user,
        city='Київ',
        address='Відділення №1',
        address_ref='ref123'
    )

    order_id = order.id
    order_items_count = order.items.count()

    # Перевіряємо що замовлення створилось
    assert Order.objects.filter(id=order_id).exists()
    assert OrderItem.objects.filter(order_id=order_id).count() == order_items_count

    # Видаляємо користувача
    user.delete()

    # Перевіряємо каскадне видалення замовлень та їх елементів
    assert not Order.objects.filter(id=order_id).exists()
    assert OrderItem.objects.filter(order_id=order_id).count() == 0


@pytest.mark.django_db
def test_product_deletion_sets_null_in_order_item(user, basket, product, category):
    """Тест що видалення товару встановлює NULL в OrderItem.product"""
    from shop.services.order import create_order_from_basket

    # Додаємо товар у кошик
    BasketItem.objects.create(basket=basket, product=product, quantity=1)

    # Створюємо замовлення
    order = create_order_from_basket(
        user=user,
        city='Київ',
        address='Відділення №1',
        address_ref='ref123'
    )

    order_item = order.items.first()
    original_price = order_item.price
    product_name = product.name

    # Перевіряємо що товар пов'язаний з замовленням
    assert order_item.product == product
    assert order_item.price == product.price

    # Видаляємо товар
    product.delete()

    # Оновлюємо об'єкт з БД
    order_item.refresh_from_db()

    # Перевіряємо що product став NULL, але ціна залишилась
    assert order_item.product is None
    assert order_item.price == original_price
    assert OrderItem.objects.filter(order=order).exists()


@pytest.mark.django_db
def test_order_relationships_integrity(user, basket, product, category):
    """Тест цілісності зв'язків між Order, OrderItem та Product"""
    from shop.services.order import create_order_from_basket

    # Створюємо другий товар
    product2 = Product.objects.create(
        name='Товар 2',
        slug='product-2',
        category=category,
        price=200.00
    )

    # Додаємо товари у кошик
    BasketItem.objects.create(basket=basket, product=product, quantity=2)
    BasketItem.objects.create(basket=basket, product=product2, quantity=3)

    # Створюємо замовлення
    order = create_order_from_basket(
        user=user,
        city='Київ',
        address='Відділення №1',
        address_ref='ref123'
    )

    # Перевіряємо зв'язки Order -> OrderItem
    assert order.items.count() == 2
    assert OrderItem.objects.filter(order=order).count() == 2

    # Перевіряємо зв'язки OrderItem -> Product
    order_item1 = order.items.get(product=product)
    order_item2 = order.items.get(product=product2)

    assert order_item1.product == product
    assert order_item2.product == product2

    # Перевіряємо зворотні зв'язки Product -> OrderItem
    assert product.order_items.filter(order=order).exists()
    assert product2.order_items.filter(order=order).exists()

    # Перевіряємо що ціни зафіксовані в момент створення замовлення
    assert order_item1.price == product.price
    assert order_item2.price == product2.price

    # Змінюємо ціни товарів
    original_price1 = product.price
    original_price2 = product2.price

    product.price = 999.99
    product.save()
    product2.price = 888.88
    product2.save()

    # Оновлюємо об'єкти з БД
    order_item1.refresh_from_db()
    order_item2.refresh_from_db()

    # Перевіряємо що ціни в замовленні не змінились
    assert order_item1.price == original_price1
    assert order_item2.price == original_price2
    assert order_item1.price != product.price
    assert order_item2.price != product2.price


@pytest.mark.django_db
def test_order_with_different_categories_and_brands(user, basket, category):
    """Тест з товарами різних категорій та брендів"""
    from shop.services.order import create_order_from_basket
    from shop.models import Brand

    # Створюємо додаткову категорію та бренди
    category2 = Category.objects.create(name='Електроніка', slug='electronics')
    brand1 = Brand.objects.create(name='Samsung', slug='samsung')
    brand2 = Brand.objects.create(name='Apple', slug='apple')

    # Створюємо товари різних категорій та брендів
    product1 = Product.objects.create(
        name='Samsung Galaxy S23',
        slug='samsung-galaxy-s23',
        category=category2,
        brand=brand1,
        price=25000.00
    )

    product2 = Product.objects.create(
        name='iPhone 15',
        slug='iphone-15',
        category=category2,
        brand=brand2,
        price=35000.00
    )

    product3 = Product.objects.create(
        name='Навушники',
        slug='headphones',
        category=category,  # Оригінальна категорія
        brand=brand1,
        price=1500.00
    )

    # Додаємо товари у кошик
    BasketItem.objects.create(basket=basket, product=product1, quantity=1)
    BasketItem.objects.create(basket=basket, product=product2, quantity=1)
    BasketItem.objects.create(basket=basket, product=product3, quantity=2)

    # Створюємо замовлення
    order = create_order_from_basket(
        user=user,
        city='Київ',
        address='Відділення №10',
        address_ref='ref456'
    )

    # Перевіряємо структуру замовлення
    assert order.items.count() == 3

    # Перевіряємо товари по категоріях
    electronics_items = order.items.filter(product__category=category2)
    other_items = order.items.filter(product__category=category)

    assert electronics_items.count() == 2  # Samsung і iPhone
    assert other_items.count() == 1  # Навушники

    # Перевіряємо товари по брендах
    samsung_items = order.items.filter(product__brand=brand1)
    apple_items = order.items.filter(product__brand=brand2)

    assert samsung_items.count() == 2  # Galaxy і навушники
    assert apple_items.count() == 1  # iPhone

    # Перевіряємо правильність розрахунків
    expected_total = (
            product1.price * 1 +  # Samsung Galaxy
            product2.price * 1 +  # iPhone
            product3.price * 2  # Навушники x2
    )
    assert order.get_total_price() == expected_total
    assert order.get_total_price() == 63000.00  # 25000 + 35000 + 3000

    # Перевіряємо що всі товари різних категорій збережені
    order_categories = set(item.product.category for item in order.items.all())
    order_brands = set(item.product.brand for item in order.items.all())

    assert len(order_categories) == 2
    assert category in order_categories
    assert category2 in order_categories

    assert len(order_brands) == 2
    assert brand1 in order_brands
    assert brand2 in order_brands


import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Product, Category, Basket, BasketItem, Order, Review
from unittest.mock import patch, Mock


@pytest.mark.django_db
class TestProductViews:
    """Тести для відображення товарів"""

    def test_product_list(self, client, category, product):
        """Базовий тест списку товарів"""
        response = client.get(reverse('shop:product_list'))
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_product_detail(self, client, category, product):
        """Тест детальної сторінки товару"""
        response = client.get(
            reverse('shop:product_detail',
                    args=[category.slug, product.slug])
        )
        assert response.status_code == 200
        assert product.name in response.content.decode()
        assert "100,00 грн." in response.content.decode()


@pytest.mark.django_db
class TestBasketViews:
    """Тести для роботи з кошиком"""

    def test_add_to_basket(self, auth_client, product):
        """Тест додавання товару в кошик"""
        response = auth_client.post(
            reverse('shop:add_to_basket', args=[product.id])
        )
        assert response.status_code == 302
        assert BasketItem.objects.filter(product=product).exists()

    def test_basket_detail(self, auth_client, basket, basket_item):
        """Тест відображення кошика"""
        response = auth_client.get(reverse('shop:basket_detail'))
        assert response.status_code == 200
        assert basket_item.product.name in response.content.decode()

    def test_update_basket_item(self, auth_client, basket_item):
        """Тест оновлення кількості товару"""
        response = auth_client.post(
            reverse('shop:update_basket_item', args=[basket_item.id]),
            {'quantity': 5}
        )
        basket_item.refresh_from_db()
        assert response.status_code == 302
        assert basket_item.quantity == 5

    def test_remove_from_basket(self, auth_client, basket_item):
        """Тест видалення товару з кошика"""
        item_id = basket_item.id
        response = auth_client.post(
            reverse('shop:remove_from_basket', args=[item_id])
        )
        assert response.status_code == 302
        assert not BasketItem.objects.filter(id=item_id).exists()

    def test_clear_basket(self, auth_client, basket, basket_item):
        """Тест очищення кошика"""
        response = auth_client.post(reverse('shop:clear_basket'))
        assert response.status_code == 302
        assert basket.items.count() == 0


@pytest.mark.django_db
class TestOrderViews:
    """Тести для замовлень"""

    def test_order_detail(self, auth_client, user):
        """Тест деталей замовлення"""
        # Створюємо тестове замовлення
        order = Order.objects.create(
            user=user,
            address='Тестова адреса',
            status='pending'
        )

        response = auth_client.get(
            reverse('shop:order_detail', args=[order.id])
        )
        assert response.status_code == 200
        assert order.address in response.content.decode()


@pytest.mark.django_db
class TestNovaPoshtaAPI:
    """Тести для API Нової Пошти"""

    @patch('shop.services.nova_poshta.requests.post')
    def test_get_nova_poshta_cities(self, mock_post, auth_client):
        """Тест отримання міст"""
        # Мокаємо відповідь API
        mock_post.return_value.json.return_value = {
            'success': True,
            'data': [{'Ref': 'ref1', 'Description': 'Київ'}]
        }

        response = auth_client.get(
            reverse('shop:get_nova_poshta_cities') + '?city=Київ'
        )
        assert response.status_code == 200
        data = response.json()
        assert 'cities' in data
        assert len(data['cities']) == 1

    @patch('shop.services.nova_poshta.requests.post')
    def test_get_nova_poshta_warehouses(self, mock_post, auth_client):
        """Тест отримання відділень"""
        mock_post.return_value.json.return_value = {
            'success': True,
            'data': [{'Ref': 'ref1', 'Description': 'Відділення №1'}]
        }

        response = auth_client.get(
            reverse('shop:get_nova_poshta_warehouses') + '?city=Київ'
        )
        assert response.status_code == 200
        data = response.json()
        assert 'warehouses' in data


@pytest.mark.django_db
class TestReviewViews:
    """Тести для відгуків"""

    def test_delete_review(self, auth_client, user, product):
        """Тест видалення відгуку"""
        # Створюємо відгук
        review = Review.objects.create(
            product=product,
            user=user,
            comment='Тестовий коментар'
        )

        response = auth_client.post(
            reverse('shop:delete_review', args=[review.id])
        )
        assert response.status_code == 302
        assert not Review.objects.filter(id=review.id).exists()
