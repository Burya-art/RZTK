from django.urls import path
from account.api_views import UserAPIView

urlpatterns = [
    path('user/', UserAPIView.as_view(), name='user-api'),
]