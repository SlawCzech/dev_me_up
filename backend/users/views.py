from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import models
from .helpers.nick_generator import generate_nick
from .permissions import IsAdminOrSelf
from .serializers import PasswordReminderSerializer, PasswordResetSerializer, CustomUserCreateSerializer


class CreateUserAPIView(CreateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()


class CustomUserWithProfileCreateAPIView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserCreateSerializer

    def create(self, request, *args, **kwargs):
        custom_user_data = request.data.copy()
        profile_data = custom_user_data.pop("profile", {})

        serializer = self.get_serializer(data=custom_user_data)
        serializer.is_valid(raise_exception=True)

        custom_user = serializer.save()
        models.UserProfile.objects.create(user=custom_user, **profile_data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class CreateAnonymousUserAPIView(APIView):
    def post(self, request):
        anonymous_user = models.AnonymousUser.objects.create()
        serializer = serializers.AnonymousUserSerializer(anonymous_user)

        return Response(serializer.data, status=201)


class RegisterUserAPIView(CreateAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = reverse("activate_user", kwargs={"uid": uid, "token": token})
        activation_link = f"http://0.0.0.0:8000{activation_link}"

        send_mail(
            subject="Account Activation",
            message=f"Please click the following link to activate your account: {activation_link}",
            from_email="noreply@your-domain.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserActivationView(APIView):
    def get(self, request, uid, token):
        user_id = force_str(urlsafe_base64_decode(uid))

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"detail": "Account activated successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


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


class UserDeactivationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def post(self, request, pk):
        user = get_user_model().objects.filter(id=pk).first()

        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            user.is_active = False
            user.save()
            return Response(
                {"message": f"{user.username} has been deactivated."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": f"{user.username} is already deactivated."},
                status=status.HTTP_200_OK,
            )


class PasswordReminderView(APIView):
    def post(self, request):
        serializer = PasswordReminderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.get(email=serializer.validated_data["email"])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://0.0.0.0:8000/api/v1/users/password-reset/{uid}/{token}/"

        send_mail(
            subject="Password Reset",
            message=f"Please click the following link to reset your password: {reset_link}",
            from_email="noreply@email.com",
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

        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response(
            {"detail": "Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
