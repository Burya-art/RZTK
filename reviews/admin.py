from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'created']
    list_filter = ['created']
    search_fields = ['user__username', 'product__name']
