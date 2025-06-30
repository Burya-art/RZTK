from rest_framework import serializers
from products.models import Product, Category, Brand


class CategorySerializer(serializers.ModelSerializer):
    """Серіалізатор для категорій товарів"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BrandSerializer(serializers.ModelSerializer):
    """Серіалізатор для брендів товарів"""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    """Серіалізатор для товарів з вкладеними категоріями і брендами"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 
            'available', 'created', 'updated', 'image',
            'category', 'brand'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Спрощений серіалізатор для списку товарів (менше даних для швидкості)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'available', 
            'image', 'category_name', 'brand_name'
        ]
