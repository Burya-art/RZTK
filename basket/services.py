from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Basket, BasketItem
from products.models import Product


class BasketService:
    """Сервіс для роботи з корзиною"""
    
    @staticmethod
    def get_or_create_basket(user: User) -> Basket:
        """Отримує або створює корзину для користувача"""
        # Знаходимо існуючу корзину або створюємо нову для користувача
        basket, created = Basket.objects.get_or_create(user=user)
        return basket
    
    @staticmethod
    def add_product_to_basket(user: User, product_id: int, quantity: int = 1) -> BasketItem:
        """Додає товар до корзини"""
        # Перевіряємо що товар існує
        product = get_object_or_404(Product, id=product_id)
        # Отримуємо корзину користувача
        basket = BasketService.get_or_create_basket(user)
        
        # Знаходимо існуючий товар в корзині або створюємо новий
        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={'quantity': quantity}  # Кількість для нового товару
        )
        
        # Якщо товар вже є в корзині - збільшуємо кількість
        if not created:
            basket_item.quantity += quantity
            basket_item.save()
        
        return basket_item
    
    @staticmethod
    def update_basket_item_quantity(user: User, item_id: int, quantity: int) -> BasketItem:
        """Оновлює кількість товару в корзині"""
        # Знаходимо товар в корзині користувача
        basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=user)
        # Оновлюємо кількість
        basket_item.quantity = quantity
        basket_item.save()
        return basket_item
    
    @staticmethod
    def remove_item_from_basket(user: User, item_id: int) -> None:
        """Видаляє товар з корзини"""
        # Знаходимо товар в корзині користувача
        basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=user)
        # Видаляємо товар з корзини
        basket_item.delete()
    
    @staticmethod
    def clear_basket(user: User) -> None:
        """Очищає корзину користувача"""
        # Знаходимо корзину користувача
        basket = get_object_or_404(Basket, user=user)
        # Видаляємо всі товари з корзини
        basket.items.all().delete()
    
    @staticmethod
    def get_basket_total_price(user: User) -> float:
        """Обчислює загальну вартість корзини"""
        # Отримуємо корзину користувача
        basket = BasketService.get_or_create_basket(user)
        # Підраховуємо загальну суму: кількість × ціна для кожного товару
        return sum(item.get_total_price() for item in basket.items.all())
    
    @staticmethod
    def is_basket_empty(user: User) -> bool:
        """Перевіряє, чи порожня корзина"""
        # Отримуємо корзину користувача
        basket = BasketService.get_or_create_basket(user)
        # Повертаємо True якщо товарів немає, False якщо є
        return not basket.items.exists()