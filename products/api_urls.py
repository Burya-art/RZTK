from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.api_views import ProductViewSet, CategoryViewSet, BrandViewSet

# Створюємо роутер який автоматично генерує URL patterns
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)

# URL patterns для API
urlpatterns = [
    path('', include(router.urls)),
]