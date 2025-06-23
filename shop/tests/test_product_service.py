import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from shop.models import Product, Category, Brand
from shop.services.product import ProductService


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def category():
    return Category.objects.create(name='Electronics', slug='electronics')


@pytest.fixture
def category2():
    return Category.objects.create(name='Books', slug='books')


@pytest.fixture
def brand():
    return Brand.objects.create(name='Samsung', slug='samsung')


@pytest.fixture
def brand2():
    return Brand.objects.create(name='Apple', slug='apple')


@pytest.fixture
def product(category, brand):
    return Product.objects.create(
        name='Samsung Phone',
        slug='samsung-phone',
        category=category,
        brand=brand,
        price=500.00,
        available=True,
        description='Great Samsung phone'
    )


@pytest.fixture
def product2(category, brand2):
    return Product.objects.create(
        name='iPhone',
        slug='iphone',
        category=category,
        brand=brand2,
        price=1000.00,
        available=True,
        description='Amazing iPhone'
    )


@pytest.fixture
def product3(category2, brand):
    return Product.objects.create(
        name='Programming Book',
        slug='programming-book',
        category=category2,
        brand=brand,
        price=50.00,
        available=True,
        description='Learn programming'
    )


@pytest.mark.django_db
class TestProductService:
    """Тести для ProductService"""

    def test_get_filtered_products_no_filters(self, product, product2, product3):
        """Тест отримання всіх доступних товарів без фільтрів"""
        products = ProductService.get_filtered_products()
        
        assert products.count() == 3
        assert product in products
        assert product2 in products
        assert product3 in products

    def test_get_filtered_products_by_category(self, product, product2, product3, category):
        """Тест фільтрації за категорією"""
        products = ProductService.get_filtered_products(category_slug=category.slug)
        
        assert products.count() == 2
        assert product in products
        assert product2 in products
        assert product3 not in products

    def test_get_filtered_products_by_brand(self, product, product2, product3, brand):
        """Тест фільтрації за брендом"""
        products = ProductService.get_filtered_products(brand_slug=brand.slug)
        
        assert products.count() == 2
        assert product in products
        assert product3 in products
        assert product2 not in products

    def test_get_filtered_products_by_search_query(self, product, product2, product3):
        """Тест пошуку за запитом"""
        # Пошук за назвою
        products = ProductService.get_filtered_products(search_query='Samsung')
        assert products.count() == 1
        assert product in products

        # Пошук за описом
        products = ProductService.get_filtered_products(search_query='programming')
        assert products.count() == 1
        assert product3 in products

    def test_get_filtered_products_by_price_range(self, product, product2, product3):
        """Тест фільтрації за діапазоном цін"""
        # Мінімальна ціна
        products = ProductService.get_filtered_products(price_min=100.0)
        assert products.count() == 2
        assert product in products
        assert product2 in products

        # Максимальна ціна
        products = ProductService.get_filtered_products(price_max=600.0)
        assert products.count() == 2
        assert product in products
        assert product3 in products

        # Діапазон цін
        products = ProductService.get_filtered_products(price_min=400.0, price_max=800.0)
        assert products.count() == 1
        assert product in products

    def test_get_filtered_products_sort_by_price(self, product, product2, product3):
        """Тест сортування за ціною"""
        # Сортування за зростанням
        products = ProductService.get_filtered_products(sort_by='price_asc')
        products_list = list(products)
        assert products_list[0] == product3  # 50.00
        assert products_list[1] == product   # 500.00
        assert products_list[2] == product2  # 1000.00

        # Сортування за спаданням
        products = ProductService.get_filtered_products(sort_by='price_desc')
        products_list = list(products)
        assert products_list[0] == product2  # 1000.00
        assert products_list[1] == product   # 500.00
        assert products_list[2] == product3  # 50.00

    def test_get_product_by_slug(self, product, category):
        """Тест отримання товару за слагом"""
        retrieved_product = ProductService.get_product_by_slug(category.slug, product.slug)
        
        assert retrieved_product == product

    def test_validate_price_range_valid(self):
        """Тест валідації коректного діапазону цін"""
        price_min, price_max, errors = ProductService.validate_price_range('100', '500')
        
        assert price_min == 100.0
        assert price_max == 500.0
        assert errors == []

    def test_validate_price_range_negative_prices(self):
        """Тест валідації від'ємних цін"""
        price_min, price_max, errors = ProductService.validate_price_range('-100', '-50')
        
        assert price_min is None
        assert price_max is None
        assert 'Мінімальна ціна не може бути від\'ємною.' in errors
        assert 'Максимальна ціна не може бути від\'ємною.' in errors

    def test_validate_price_range_invalid_format(self):
        """Тест валідації некоректного формату цін"""
        price_min, price_max, errors = ProductService.validate_price_range('abc', 'def')
        
        assert price_min is None
        assert price_max is None
        assert 'Некоректний формат цін.' in errors

    def test_validate_price_range_min_greater_than_max(self):
        """Тест валідації коли мінімальна ціна більша за максимальну"""
        price_min, price_max, errors = ProductService.validate_price_range('500', '100')
        
        assert price_min == 500.0
        assert price_max == 100.0
        assert 'Мінімальна ціна не може бути більшою за максимальну.' in errors

    def test_track_product_view_authenticated_user(self, user, product):
        """Тест відстеження перегляду товару авторизованим користувачем"""
        # Очищуємо кеш
        cache.clear()
        
        ProductService.track_product_view(user, product)
        
        viewed_products = cache.get(f'viewed_products_{user.id}', [])
        product_viewed = cache.get(f'product_viewed_{user.id}', False)
        
        assert product.id in viewed_products
        assert product_viewed is True

    def test_track_product_view_unauthenticated_user(self, product):
        """Тест відстеження перегляду товару неавторизованим користувачем"""
        from django.contrib.auth.models import AnonymousUser
        
        user = AnonymousUser()
        
        # Не повинно викидати помилку
        ProductService.track_product_view(user, product)
        
        # Перевіряємо що нічого не збережено
        viewed_products = cache.get(f'viewed_products_{user.id}', [])
        assert viewed_products == []

    def test_track_product_view_limit_to_10(self, user, category, brand):
        """Тест обмеження списку переглянутих товарів до 10"""
        # Очищуємо кеш
        cache.clear()
        
        # Створюємо 12 товарів
        products = []
        for i in range(12):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=category,
                brand=brand,
                price=100.00,
                available=True
            )
            products.append(product)
            ProductService.track_product_view(user, product)
        
        viewed_products = cache.get(f'viewed_products_{user.id}', [])
        
        # Повинно бути максимум 10 товарів
        assert len(viewed_products) == 10
        # Перші 2 товари повинні бути видалені
        assert products[0].id not in viewed_products
        assert products[1].id not in viewed_products
        # Останні 10 товарів повинні залишитися
        assert products[11].id in viewed_products

    def test_get_recommended_products_no_viewed_products(self, user):
        """Тест рекомендацій без переглянутих товарів"""
        cache.clear()
        
        recommended = ProductService.get_recommended_products(user)
        
        assert recommended is None

    def test_get_recommended_products_with_viewed_products(self, user, product, product2, category, brand):
        """Тест рекомендацій на основі переглянутих товарів"""
        # Очищуємо кеш
        cache.clear()
        
        # Створюємо додатковий товар тієї ж категорії та бренду
        recommended_product = Product.objects.create(
            name='Recommended Product',
            slug='recommended-product',
            category=category,
            brand=brand,
            price=300.00,
            available=True
        )
        
        # Відстежуємо перегляд товару
        ProductService.track_product_view(user, product)
        
        # Викликаємо рекомендації
        recommended = ProductService.get_recommended_products(user)
        
        # Перевіряємо що рекомендований товар присутній
        assert recommended_product in recommended
        # Переглянутий товар не повинен бути в рекомендаціях
        assert product not in recommended

    def test_get_recommended_products_unauthenticated_user(self, product):
        """Тест рекомендацій для неавторизованого користувача"""
        from django.contrib.auth.models import AnonymousUser
        
        user = AnonymousUser()
        recommended = ProductService.get_recommended_products(user)
        
        assert recommended is None

    def test_complex_filtering(self, product, product2, product3, category, brand):
        """Тест комплексної фільтрації з кількома критеріями"""
        products = ProductService.get_filtered_products(
            category_slug=category.slug,
            brand_slug=brand.slug,
            search_query='Samsung',
            price_min=400.0,
            price_max=600.0,
            sort_by='price_asc'
        )
        
        assert products.count() == 1
        assert product in products