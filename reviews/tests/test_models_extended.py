import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from reviews.models import Review


class TestReviewValidation:
    """Прості тести для валідації відгуків"""

    @pytest.mark.django_db
    def test_unique_user_product_review(self, user, product):
        """Користувач може залишити тільки один відгук на продукт"""
        # Створюємо перший відгук
        Review.objects.create(
            user=user, product=product, comment="Перший відгук"
        )

        # Спроба створити другий відгук від того ж користувача
        with pytest.raises(IntegrityError):
            Review.objects.create(
                user=user, product=product, comment="Другий відгук"
            )

    @pytest.mark.django_db
    def test_empty_comment_allowed(self, user, product):
        """Відгук може бути без коментаря"""
        review = Review.objects.create(
            user=user, product=product, comment=""
        )
        assert review.comment == ""
        assert review.id is not None

    def test_review_table_name(self):
        """Перевірка назви таблиці"""
        assert Review._meta.db_table == 'reviews'
