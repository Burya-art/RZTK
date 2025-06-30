import pytest
from django.contrib.auth.models import User
from reviews.models import Review


@pytest.mark.django_db
class TestReviewModels:
    """Базові тести для моделей відгуків"""
    
    def test_review_creation(self, review):
        """Тест створення відгуку"""
        assert review.comment == "Дуже хороший продукт!"
        assert review.user.username == "testuser"
        assert review.product.name == "Тестовий продукт"
        assert review.created is not None
    
    def test_review_str_method(self, review):
        """Тест методу __str__ відгуку"""
        expected = "Відгук від testuser на Тестовий продукт"
        assert str(review) == expected
    
    def test_review_relationships(self, review, user, product):
        """Тест зв'язків між моделями"""
        assert review.user == user
        assert review.product == product
        assert review in user.user_reviews.all()
        assert review in product.reviews.all()
    
    def test_review_ordering(self, product):
        """Тест сортування відгуків за датою створення"""
        # Створюємо двох різних користувачів
        user1 = User.objects.create_user("user1", "user1@test.com", "pass")
        user2 = User.objects.create_user("user2", "user2@test.com", "pass")
        
        review1 = Review.objects.create(
            user=user1, product=product, comment="Перший відгук"
        )
        review2 = Review.objects.create(
            user=user2, product=product, comment="Другий відгук"
        )
        
        # Останній створений відгук повинен бути першим (ordering = ['-created'])
        reviews = Review.objects.all()
        assert reviews.first() == review2
        assert reviews.last() == review1