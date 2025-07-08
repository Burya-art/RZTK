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
        """Called before social login processing"""
        # For existing users, we need to update their profile here
        # since save_user is only called for new users
        if sociallogin.account.provider == 'google':
            # Check if this is an existing user (has pk)
            if sociallogin.account.pk:
                self.populate_user_profile_from_google(sociallogin.account.user, sociallogin)
        
        # Call parent method
        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        """Called to populate user data from social login"""
        user = super().populate_user(request, sociallogin, data)
        return user
