from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Review
from products.models import Product


class ReviewService:
    """Сервіс для роботи з відгуками"""
    
    @staticmethod
    def create_review(user: User, product: Product, comment: str, rating: int = None) -> tuple:
        """
        Створює новий відгук для продукту.
        Повертає (review, success, error_message)
        """
        try:
            review = Review.objects.create(
                user=user,
                product=product,
                comment=comment
            )
            return review, True, None
        except IntegrityError:
            return None, False, 'Ви вже залишили відгук для цього товару.'
    
    @staticmethod
    def delete_review(user: User, review_id: int) -> tuple:
        """
        Видаляє відгук користувача.
        Повертає (success, product, error_message)
        """
        try:
            review = get_object_or_404(Review, id=review_id, user=user)
            product = review.product
            review.delete()
            return True, product, None
        except:
            return False, None, 'Відгук не знайдено або немає прав для видалення.'
    
    @staticmethod
    def get_product_reviews(product: Product):
        """Отримує всі відгуки для продукту"""
        return product.reviews.all().order_by('-created')
    
    @staticmethod
    def user_has_review(user: User, product: Product) -> bool:
        """Перевіряєз чи користувач вже залишив відгук для цього товару"""
        if not user.is_authenticated:
            return False
        return Review.objects.filter(user=user, product=product).exists()
    
    @staticmethod
    def get_user_reviews(user: User):
        """Отримує всі відгуки користувача"""
        return Review.objects.filter(user=user).order_by('-created')