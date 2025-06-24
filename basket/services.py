from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Basket, BasketItem
from products.models import Product


class BasketService:
    """Сервіс для роботи з корзиною"""
    
    @staticmethod
    def get_or_create_basket(user: User) -> Basket:
        """Отримує або створює корзину для користувача"""
        basket, created = Basket.objects.get_or_create(user=user)
        return basket
    
    @staticmethod
    def add_product_to_basket(user: User, product_id: int, quantity: int = 1) -> BasketItem:
        """Додає товар до корзини"""
        product = get_object_or_404(Product, id=product_id)
        basket = BasketService.get_or_create_basket(user)
        
        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            basket_item.quantity += quantity
            basket_item.save()
        
        return basket_item
    
    @staticmethod
    def update_basket_item_quantity(user: User, item_id: int, quantity: int) -> BasketItem:
        """Оновлює кількість товару в корзині"""
        basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=user)
        basket_item.quantity = quantity
        basket_item.save()
        return basket_item
    
    @staticmethod
    def remove_item_from_basket(user: User, item_id: int) -> None:
        """Видаляє товар з корзини"""
        basket_item = get_object_or_404(BasketItem, id=item_id, basket__user=user)
        basket_item.delete()
    
    @staticmethod
    def clear_basket(user: User) -> None:
        """Очищає корзину користувача"""
        basket = get_object_or_404(Basket, user=user)
        basket.items.all().delete()
    
    @staticmethod
    def get_basket_total_price(user: User) -> float:
        """Обчислює загальну вартість корзини"""
        basket = BasketService.get_or_create_basket(user)
        return sum(item.get_total_price() for item in basket.items.all())
    
    @staticmethod
    def is_basket_empty(user: User) -> bool:
        """Перевіряє, чи порожня корзина"""
        basket = BasketService.get_or_create_basket(user)
        return not basket.items.exists()