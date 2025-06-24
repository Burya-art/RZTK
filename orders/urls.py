from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('nova-poshta/cities/', views.get_nova_poshta_cities, name='get_nova_poshta_cities'),
    path('nova-poshta/warehouses/', views.get_nova_poshta_warehouses, name='get_nova_poshta_warehouses'),
]