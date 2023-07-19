from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import UpdateAPIView, ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import models
from .helpers.nick_generator import generate_nick
from .permissions import IsAdminOrSelf
from .serializers import PasswordReminderSerializer, PasswordResetSerializer


class CreateUserAPIView(CreateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()


class CustomNickAPIView(APIView):
    def get(self, request):
        nick = generate_nick()
        return Response(nick, status=status.HTTP_200_OK)


class GetUserAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    queryset = get_user_model().objects.all()
    serializer_class = serializers.CustomUserSerializer


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_object(self):
        return self.request.user


class DeleteUserAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    queryset = get_user_model().objects.all()
    serializer_class = serializers.CustomUserSerializer


class PasswordReminderView(APIView):
    def post(self, request):
        serializer = PasswordReminderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.get(email=serializer.validated_data['email'])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://0.0.0.0:8000/api/v1/users/password-reset/{uid}/{token}/"

        send_mail(
            subject="Password Reset",
            message=f"Please click the following link to reset your password: {reset_link}",
            from_email="noreply@your-domain.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(APIView):
    def post(self, request, uid, token):
        user_id = force_str(urlsafe_base64_decode(uid))

        try:
            user = models.CustomUser.objects.get(pk=user_id)
        except models.CustomUser.DoesNotExist:
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['password'])
        user.save()

        return Response(
            {"detail": "Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
