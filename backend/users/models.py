import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"),
        max_length=50,
        unique=False,
        help_text=_("Required. 50 characters or fewer."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active." "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class AnonymousUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anonymous user {self.id}"


class UserProfile(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="profile")
    rank = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    is_search_visible = models.BooleanField(default=False)
    is_rank_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user}"
