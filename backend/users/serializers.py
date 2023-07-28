from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        exclude = ("user",)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "password",
            "profile",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password")

        if profile_data:
            custom_user = get_user_model().objects.create_user(password=password, **validated_data)
            models.UserProfile.objects.create(user=custom_user, **profile_data)
            custom_user = get_user_model().objects.select_related("profile").get(user_id=custom_user.pk)
        else:
            custom_user = get_user_model().objects.create_user(password=password, **validated_data)

        return custom_user


class CustomUserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    games_played = serializers.SerializerMethodField()
    games_won = serializers.SerializerMethodField()
    games_lost = serializers.SerializerMethodField()
    is_search_visible = serializers.SerializerMethodField()
    is_rank_visible = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "rank",
            "games_played",
            "games_won",
            "games_lost",
            "is_search_visible",
            "is_rank_visible",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance

    def get_rank(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.rank
        except IndexError:
            return None

    def get_games_played(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.games_played
        except IndexError:
            return None

    def get_games_won(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.games_won
        except IndexError:
            return None

    def get_games_lost(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.games_lost
        except IndexError:
            return None

    def get_is_search_visible(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.is_search_visible
        except IndexError:
            return None

    def get_is_rank_visible(self, obj):
        try:
            profile = obj.profile.all()[0]
            return profile.is_rank_visible
        except IndexError:
            return None


class PasswordReminderSerializer(serializers.Serializer):
    email = serializers.EmailField()
    User = get_user_model()

    def validate_email(self, value):
        try:
            self.User.objects.get(email=value)
        except self.User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class AnonymousUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnonymousUser
        fields = "__all__"
