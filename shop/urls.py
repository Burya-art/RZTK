from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('add-to-basket/<int:product_id>/', views.add_to_basket, name='add_to_basket'),
    path('basket/', views.basket_detail, name='basket_detail'),
    path('update-basket-item/<int:item_id>/', views.update_basket_item,
         name='update_basket_item'),
    path('remove-from-basket/<int:item_id>/', views.remove_from_basket,
         name='remove_from_basket'),
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]
