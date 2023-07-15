from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views
from .views import CustomNickAPIView

urlpatterns = [
    path('users/', views.CreateUserAPIView.as_view(), name='create_user'),
    path('users/<int:pk>', views.GetUserAPIView.as_view(), name='get_user'),
    path('users/update/', views.UserUpdateAPIView.as_view(), name='update_user'),
    path('users/custom-nick/', CustomNickAPIView.as_view(), name='generate_nick'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
