from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from products.api_views import ProductViewSet, CategoryViewSet, BrandViewSet

# Створюємо роутер який автоматично генерує URL patterns
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)


@api_view(['GET'])
def api_root(request):
    """Головна сторінка API з посиланнями на всі ендпоінти"""
    return Response({
        'message': 'RZTK API',
        'endpoints': {
            'products': request.build_absolute_uri('/api/products/'),
            'categories': request.build_absolute_uri('/api/categories/'),
            'brands': request.build_absolute_uri('/api/brands/'),
            'user': request.build_absolute_uri('/api/account/user/'),
        }
    })


# URL patterns для API
urlpatterns = [
    # Головна сторінка API замість стандартного роутера
    path('', api_root, name='api-root'),
    # Включаємо URLs з роутера
    path('', include(router.urls)),
]