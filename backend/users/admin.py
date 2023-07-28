from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import AnonymousUser, UserProfile

User = get_user_model()


class UserProfileAdminInline(admin.StackedInline):
    model = UserProfile


class UserAdminConfig(UserAdmin):
    """Customized configuration for admin panel prepared for :class:`users.models.CustomUser` model.
    If order of fields in admin panel is not to your liking
    it can be changed in list_display class field.
    """

    inlines = [UserProfileAdminInline]
    model = User
    search_fields = ("email", "username")
    list_filter = ("email", "username", "is_active", "is_staff")
    ordering = ("-last_login",)
    list_display = ("email", "username", "is_active", "is_staff", "user_profile_link")
    readonly_fields = ("date_joined",)

    def user_profile_link(self, obj):
        try:
            profile = obj.profile.all()[0]
            profile_url = reverse(f"admin:{profile._meta.app_label}_{'userprofile'}_change", args=[profile.pk])
            return format_html(f'<a href="{profile_url}">{profile}</a>')
        except IndexError:
            return None

    user_profile_link.short_description = "User Profile"


class AnonymousUserAdminConfig(admin.ModelAdmin):
    model = AnonymousUser
    list_display = ("id", "created_at")
    ordering = ("-created_at",)
    list_filter = ("created_at",)


class UserProfileAdminConfig(admin.ModelAdmin):
    fields = ("user", "rank", "is_bot", "is_online", "is_search_visible", "is_rank_visible")
    list_display = (
        "pk",
        "rank",
        "games_played",
        "games_won",
        "games_lost",
        "is_bot",
        "is_online",
        "is_search_visible",
        "is_rank_visible",
    )
    search_fields = ("is_bot",)
    list_filter = ("is_bot", "is_online")
    ordering = ("-rank",)


admin.site.register(User, UserAdminConfig)
admin.site.register(AnonymousUser, AnonymousUserAdminConfig)
admin.site.register(UserProfile, UserProfileAdminConfig)
