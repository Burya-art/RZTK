from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserAPIView(APIView):

    def get(self, request):
        """Отримати інформацію про поточного користувача"""
        if request.user.is_authenticated:
            user_data = {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_authenticated': True
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'is_authenticated': False,
                'message': 'Користувач не авторизований'
            }, status=status.HTTP_401_UNAUTHORIZED)
