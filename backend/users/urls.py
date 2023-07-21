from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path("users/", views.CreateUserAPIView.as_view(), name="create_user"),
    path("register/", views.RegisterUserAPIView.as_view(), name="register_user"),
    path(
        "activate/<str:uid>/<str:token>/",
        views.UserActivationView.as_view(),
        name="activate_user",
    ),
    path("users/create_anonymous_user/", views.CreateAnonymousUserAPIView.as_view(), name="create_anonymous_user"),
    path("users/<int:pk>", views.GetUserAPIView.as_view(), name="get_user"),
    path("users/update/", views.UserUpdateAPIView.as_view(), name="update_user"),
    path("users/custom-nick/", views.CustomNickAPIView.as_view(), name="generate_nick"),
    path("users/delete/<int:pk>", views.DeleteUserAPIView.as_view(), name="delete_user"),
    path(
        "users/deactivate/<int:pk>/",
        views.UserDeactivationAPIView.as_view(),
        name="deactivate_user",
    ),
    path(
        "users/password-reset/",
        views.PasswordReminderView.as_view(),
        name="password_reminder",
    ),
    path(
        "users/password-reset/<str:uid>/<str:token>/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
