from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import UpdateAPIView, ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers
from .permissions import IsAdminOrSelf


class CreateUserAPIView(CreateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()


class GetUserAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    queryset = get_user_model().objects.all()
    serializer_class = serializers.CustomUserSerializer


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
