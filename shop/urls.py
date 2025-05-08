from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('add-to-basket/<int:product_id>/', views.add_to_basket, name='add_to_basket'),  # додає товар до кошика
    path('basket/', views.basket_detail, name='basket_detail'),  # показує вміст кошика
    path('update-basket-item/<int:item_id>/', views.update_basket_item,
         name='update_basket_item'),  # оновлює кількість товару в кошику
    path('remove-from-basket/<int:item_id>/', views.remove_from_basket,
         name='remove_from_basket'),  # видаляє товар із кошика
    path('create-order/', views.create_order, name='create_order'),  # маршрут для створення замовлення
    path('clear-basket/', views.clear_basket, name='clear_basket'),  # маршрут для очищення кошика
    path('', views.product_list, name='product_list'),  # показує всі товари
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),  # показує товари конкретної категорії
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),  # детальна сторінка товару
]

