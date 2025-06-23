import pytest
from django.contrib.auth.models import User
from shop.models import Product, Category, Review
from shop.services.review import ReviewService


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def user2():
    return User.objects.create_user(username='testuser2', password='12345')


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


@pytest.mark.django_db
class TestReviewServiceSimple:
    """Спрощені тести для ReviewService"""

    def test_create_review_success(self, user, product):
        """Тест успішного створення відгуку"""
        review, success, error_message = ReviewService.create_review(
            user=user,
            product=product,
            comment='Excellent product!'
        )
        
        assert success is True
        assert error_message is None
        assert review.user == user
        assert review.product == product
        assert review.comment == 'Excellent product!'

    def test_delete_review_success(self, user, product):
        """Тест успішного видалення відгуку"""
        # Створюємо відгук
        review = Review.objects.create(
            user=user,
            product=product,
            comment='Test review'
        )
        
        # Видаляємо відгук
        success, returned_product, error_message = ReviewService.delete_review(user, review.id)
        
        assert success is True
        assert returned_product == product
        assert error_message is None
        assert not Review.objects.filter(id=review.id).exists()

    def test_get_product_reviews(self, user, user2, product):
        """Тест отримання всіх відгуків для продукту"""
        # Створюємо кілька відгуків
        review1 = Review.objects.create(
            user=user,
            product=product,
            comment='Great!'
        )
        
        review2 = Review.objects.create(
            user=user2,
            product=product,
            comment='Good!'
        )
        
        reviews = ReviewService.get_product_reviews(product)
        
        assert reviews.count() == 2
        assert review1 in reviews
        assert review2 in reviews

    def test_user_has_review_true(self, user, product):
        """Тест перевірки чи є відгук у користувача (є)"""
        Review.objects.create(
            user=user,
            product=product,
            comment='Test review'
        )
        
        has_review = ReviewService.user_has_review(user, product)
        
        assert has_review is True

    def test_user_has_review_false(self, user, product):
        """Тест перевірки чи є відгук у користувача (немає)"""
        has_review = ReviewService.user_has_review(user, product)
        
        assert has_review is False

    def test_get_user_reviews(self, user, product, category):
        """Тест отримання всіх відгуків користувача"""
        # Створюємо другий продукт
        product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            category=category,
            price=200.00,
            available=True
        )
        
        # Створюємо відгуки для різних продуктів
        review1 = Review.objects.create(
            user=user,
            product=product,
            comment='Review 1'
        )
        
        review2 = Review.objects.create(
            user=user,
            product=product2,
            comment='Review 2'
        )
        
        user_reviews = ReviewService.get_user_reviews(user)
        
        assert user_reviews.count() == 2
        assert review1 in user_reviews
        assert review2 in user_reviews