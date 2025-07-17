from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment/<int:order_id>/', views.payment_form, name='payment_form'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
]
