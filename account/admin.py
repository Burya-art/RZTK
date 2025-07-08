from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('avatar',)


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'has_avatar')
    list_filter = ('user__date_joined',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)

    def has_avatar(self, obj):
        return bool(obj.avatar)

    has_avatar.boolean = True
    has_avatar.short_description = 'Has Avatar'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'uid', 'has_picture', 'last_login')
    list_filter = ('provider', 'last_login')
    search_fields = ('user__username', 'user__email', 'uid')
    readonly_fields = ('user', 'provider', 'uid', 'extra_data')

    def has_picture(self, obj):
        return 'picture' in obj.extra_data

    has_picture.boolean = True
    has_picture.short_description = 'Has Picture URL'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Розширення стандартного User admin з профілем
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Покращена адміністрація Social Accounts
admin.site.unregister(SocialAccount)
admin.site.register(SocialAccount, SocialAccountAdmin)
