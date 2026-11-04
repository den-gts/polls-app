from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

class HeaderAuthentication(BaseAuthentication):
    def authenticate(self, request):

        username = request.META.get('HTTP_X_USER')
        if not username:
            return None

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return user, None
        except User.DoesNotExist:
            raise AuthenticationFailed(f'Пользователь {username} не найден')