from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from account.models import UserProfile
import requests


class GoogleSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        # Викликаємо стандартний метод створення користувача
        user = super().save_user(request, sociallogin, form)

        # Якщо це Google OAuth
        if sociallogin.account.provider == 'google':
            self.populate_user_profile_from_google(user, sociallogin)

        return user

    def populate_user_profile_from_google(self, user, sociallogin):
        """Заповнюємо профіль користувача даними з Google"""
        try:
            # Отримуємо дані з Google
            google_data = sociallogin.account.extra_data

            # Отримуємо або створюємо профіль
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Зберігаємо аватар якщо є
            if 'picture' in google_data:
                profile.avatar = google_data['picture']
                profile.save()

        except Exception as e:
            pass

    def pre_social_login(self, request, sociallogin):
        """Викликається перед обробкою соціального входу"""
        # Для існуючих користувачів потрібно оновити профіль тут
        # оскільки save_user викликається тільки для нових користувачів
        if sociallogin.account.provider == 'google':
            # Перевіряємо чи це існуючий користувач (має pk)
            if sociallogin.account.pk:
                self.populate_user_profile_from_google(sociallogin.account.user, sociallogin)

        # Викликаємо батьківський метод
        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        """Викликається для заповнення даних користувача з соціального входу"""
        user = super().populate_user(request, sociallogin, data)

        if sociallogin.account.provider == 'google':
            google_data = sociallogin.account.extra_data

            if not user.first_name and 'given_name' in google_data:
                user.first_name = google_data['given_name']

            if not user.last_name and 'family_name' in google_data:
                user.last_name = google_data['family_name']

        return user
