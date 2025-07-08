from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="RZTK API",
        default_version='v1',
        description="API для інтернет-магазину техніки RZTK",
        terms_of_service="https://rztk.com/terms/",
        contact=openapi.Contact(email="admin@rztk.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='api-docs'),
    path('api/', include('products.api_urls')),  # Products API
    path('api/account/', include('account.api_urls')),  # User API
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('account/', include('account.urls')),  # Наші сторінки
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('basket/', include('basket.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('nova-poshta/', include('nova_poshta.urls')),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
