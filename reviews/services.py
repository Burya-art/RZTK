from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Review
from products.models import Product


class ReviewService:
    """Сервіс для роботи з відгуками"""
    
    @staticmethod
    def create_review(user: User, product: Product, comment: str) -> tuple:
        """
        Створює новий відгук для продукту.
        Повертає (review, success, error_message)
        """
        try:
            # Створюємо новий відгук
            review = Review.objects.create(
                user=user,
                product=product,
                comment=comment
            )
            return review, True, None
        except IntegrityError:
            # Обробляємо помилку унікальності (unique_together)
            return None, False, 'Ви вже залишили відгук для цього товару.'
    
    @staticmethod
    def delete_review(user: User, review_id: int) -> tuple:
        """
        Видаляє відгук користувача.
        Повертає (success, product, error_message)
        """
        try:
            # Знаходимо відгук за ID та перевіряємо власника
            review = get_object_or_404(Review, id=review_id, user=user)
            # Зберігаємо посилання на продукт для редиректу
            product = review.product
            # Видаляємо відгук
            review.delete()
            return True, product, None
        except:
            # Обробляємо всі винятки (не знайшли або немає прав)
            return False, None, 'Відгук не знайдено або немає прав для видалення.'
    
    @staticmethod
    def get_product_reviews(product: Product):
        """Отримує всі відгуки для продукту"""
        # Повертаємо всі відгуки продукту, відсортовані за датою (новіші спочатку)
        return product.reviews.all().order_by('-created')
    
    @staticmethod
    def user_has_review(user: User, product: Product) -> bool:
        """Перевіряє чи користувач вже залишив відгук для цього товару"""
        # Перевіряємо чи користувач авторизований
        if not user.is_authenticated:
            return False
        # Перевіряємо чи є відгук від цього користувача для цього товару
        return Review.objects.filter(user=user, product=product).exists()
    
    @staticmethod
    def get_user_reviews(user: User):
        """Отримує всі відгуки користувача"""
        # Повертаємо всі відгуки користувача, відсортовані за датою (новіші спочатку)
        return Review.objects.filter(user=user).order_by('-created')