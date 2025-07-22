from django.contrib import admin
from .models import Category, Product, Brand, Tag


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
    list_display = ['name', 'category', 'price', 'available', 'get_tags']
    list_filter = ['category', 'brand', 'available', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags']

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['color']