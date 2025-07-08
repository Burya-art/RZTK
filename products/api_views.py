from rest_framework import viewsets, filters

from products.models import Product, Category, Brand
from products.serializers import (
    ProductSerializer, 
    ProductListSerializer,
    CategorySerializer,
    BrandSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для категорій товарів"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """API для брендів товарів"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API для товарів з пошуком і сортуванням"""
    queryset = Product.objects.select_related('category', 'brand').filter(available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    # Пошук і сортування
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created', 'name']
    ordering = ['-created']
