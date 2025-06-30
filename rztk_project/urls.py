from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.api_urls')),  # API endpoints
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('account/', include('account.urls')),
    path('basket/', include('basket.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('nova-poshta/', include('nova_poshta.urls')),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
