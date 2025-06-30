from django.urls import path
from . import views

app_name = 'nova_poshta'

urlpatterns = [
    path('cities/', views.get_cities, name='get_cities'),
    path('warehouses/', views.get_warehouses, name='get_warehouses'),
]