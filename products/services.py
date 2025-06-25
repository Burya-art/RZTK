from typing import List, Optional
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import Product, Category, Brand


class ProductService:
    """Сервіс для роботи з продуктами"""
    
    @staticmethod
    def get_filtered_products(
        category_slug: Optional[str] = None,
        brand_slug: Optional[str] = None,
        search_query: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort_by: Optional[str] = None
    ) -> List[Product]:
        """Застосовує фільтри та повертає відфільтровані продукти"""
        products = Product.objects.filter(available=True)
        
        # Фільтр за текстом: шукаємо в назві та описі товару
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        
        # Фільтр за категорією
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        
        # Фільтр за брендом
        if brand_slug:
            brand = get_object_or_404(Brand, slug=brand_slug)
            products = products.filter(brand=brand)
        
        # Фільтр за мінімальною ціною (ціна >= price_min)
        if price_min is not None:
            products = products.filter(price__gte=price_min)
        
        # Фільтр за максимальною ціною (ціна <= price_max)
        if price_max is not None:
            products = products.filter(price__lte=price_max)
        
        # Сортування за ціною
        if sort_by == 'price_asc':
            products = products.order_by('price')      # Від дешевих до дорогих
        elif sort_by == 'price_desc':
            products = products.order_by('-price')     # Від дорогих до дешевих
        
        return products
    
    @staticmethod
    def get_product_by_slug(category_slug: str, product_slug: str) -> Product:
        """Знаходить конкретний продукт за URL слагами"""
        # Перевіряємо що категорія існує
        category = get_object_or_404(Category, slug=category_slug)
        # Шукаємо продукт в цій категорії за слагом (тільки доступні)
        return get_object_or_404(Product, category=category, slug=product_slug, available=True)
    
    @staticmethod
    def get_recommended_products(user: User) -> Optional[List[Product]]:
        """Отримує рекомендовані продукти для користувача"""
        # Рекомендації тільки для авторизованих користувачів
        if not user.is_authenticated:
            return None
        
        # Отримуємо список ID товарів, які переглядав користувач
        viewed_product_ids = cache.get(f'viewed_products_{user.id}', [])
        cache_key = f'recommended_products_{user.id}'
        
        # Якщо користувач щось переглядав і є флаг оновлення рекомендацій
        if viewed_product_ids and cache.get(f'product_viewed_{user.id}', False):
            # Отримуємо переглянуті товари
            viewed_products = Product.objects.filter(id__in=viewed_product_ids, available=True)
            # Знаходимо унікальні комбінації категорій та брендів переглянутих товарів
            viewed_combinations = viewed_products.values('category_id', 'brand_id').distinct()
            
            # Будуємо запит для пошуку схожих товарів
            query = Q()
            for combo in viewed_combinations:
                # Додаємо умову: товари з тими ж категоріями та брендами
                query |= Q(category_id=combo['category_id'], brand_id=combo['brand_id'])
            
            # Знаходимо схожі товари, виключаючи вже переглянуті
            recommended_products = Product.objects.filter(query, available=True).exclude(
                id__in=viewed_product_ids).order_by('?')[:6]  # Випадковий порядок, максимум 6 товарів
            
            # Зберігаємо рекомендації в кеші на 30 днів
            cache.set(cache_key, [p.id for p in recommended_products], timeout=3600 * 24 * 30)
            # Скидаємо флаг оновлення рекомендацій
            cache.set(f'product_viewed_{user.id}', False, timeout=3600 * 24 * 30)
            
            return recommended_products
        else:
            # Якщо немає нових переглядів, повертаємо збережені рекомендації
            recommended_product_ids = cache.get(cache_key, [])
            if recommended_product_ids:
                return Product.objects.filter(id__in=recommended_product_ids, available=True)
        
        return None
    
    @staticmethod
    def track_product_view(user: User, product: Product) -> None:
        """Відстежує перегляд продукту користувачем"""
        # Трекінг тільки для авторизованих користувачів
        if not user.is_authenticated:
            return
        
        # Отримуємо список переглянутих товарів з кешу
        viewed_products = cache.get(f'viewed_products_{user.id}', [])
        
        # Якщо цей товар ще не переглядався
        if product.id not in viewed_products:
            # Додаємо ID товару до списку переглянутих
            viewed_products.append(product.id)
            # Обмежуємо історію 10 останніми товарами (видаляємо найстарший)
            if len(viewed_products) > 10:
                viewed_products.pop(0)
            # Зберігаємо оновлений список в кеші на 30 днів
            cache.set(f'viewed_products_{user.id}', viewed_products, timeout=3600 * 24 * 30)
        
        # Встановлюємо флаг, що користувач переглянув щось нове (для оновлення рекомендацій)
        cache.set(f'product_viewed_{user.id}', True, timeout=3600 * 24 * 30)
    
    @staticmethod
    def validate_price_range(price_min: Optional[str], price_max: Optional[str]) -> tuple:
        """Валідує діапазон цін"""
        errors = []
        
        try:
            # Перевіряємо мінімальну ціну
            if price_min:
                price_min = float(price_min)  # Конвертуємо в число
                if price_min < 0:
                    errors.append('Мінімальна ціна не може бути від\'ємною.')
                    price_min = None
            else:
                price_min = None
                
            # Перевіряємо максимальну ціну
            if price_max:
                price_max = float(price_max)  # Конвертуємо в число
                if price_max < 0:
                    errors.append('Максимальна ціна не може бути від\'ємною.')
                    price_max = None
            else:
                price_max = None
                
            # Перевіряємо логічність діапазону (мін <= макс)
            if price_min is not None and price_max is not None and price_min > price_max:
                errors.append('Мінімальна ціна не може бути більшою за максимальну.')
                
        except ValueError:
            # Якщо не вдалося перетворити в число
            errors.append('Некоректний формат цін.')
            price_min = None
            price_max = None
        
        # Повертаємо очищені значення та список помилок
        return price_min, price_max, errors