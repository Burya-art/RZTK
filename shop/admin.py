from django.contrib import admin
from .models import Category, Product, Brand, Basket, BasketItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available']
    list_filter = ['category', 'brand', 'available']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'updated']


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ['basket', 'product', 'quantity', 'added_at']






