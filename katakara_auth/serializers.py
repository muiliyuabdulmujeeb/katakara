import os
from pathlib import Path
from datetime import timedelta
import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import Token, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import BannedUser, KatakaraUser, Role, RoleUpgradeRequest



env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    """Custom JWT generation serializer"""

    @classmethod
    def get_token(cls, user) -> Token:
        token =  super().get_token(user)

        if user.is_superuser:
            role = "superuser"
        else:
            group_names = set(user.groups.values_list("name", flat=True))

            if "admin" in group_names:
                role = "admin"
            elif "seller" in group_names:
                role = "seller"
            else:
                role = "buyer"
        
        token["role"] = role
        return token
    
class SignupSerializer(serializers.ModelSerializer):
    """Sign up serializer responsible for validating input, safey creating user and assigning allowed roles (buyer and seller in this case)"""

    password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=["buyer", "seller"]),
        required=False
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "roles"]


    def validate_roles(self, value):
        if not value:
            return ["buyer"]

        unique_roles = set(value)
        allowed_roles = {"buyer", "seller"}

        if not unique_roles.issubset(allowed_roles):
            raise serializers.ValidationError("Invalid role selection.")

        return list(unique_roles)

    
    def create(self, validated_data):
        roles = validated_data.pop("roles", ["buyer"])
        password = validated_data.pop("password")

        # Create user
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # Fetch Role and Group objects
        role_objects = Role.objects.filter(name__in=roles)
        group_objects = Group.objects.filter(name__in=roles)

        # Assign roles and groups (ManyToMany must be done after save)
        user.role.set(role_objects)
        user.groups.set(group_objects)

        return user

class LogoutSerializer(serializers.Serializer):
    """Logout serializer"""
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get("refresh")

        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token")

        return attrs

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Handles refresh token rotation and returns:
    - new access token
    - new refresh token
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password serializer that handles validating input and generating tokens"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        self.user = user
        return value

    def save(self):
        user = self.user
        token_generator = PasswordResetTokenGenerator()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        # Example link (frontend can handle)
        reset_link = f"http://{env('BASE_URL')}/reset-password/{uid}/{token}/"

        return {"uid": uid, "token": token, "reset_link": reset_link}

class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer that validates token used to change passowrd is correct and changes the password"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid user or token")

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired token")

        self.user = user
        return attrs

    def save(self):
        password = self.validated_data["new_password"]
        self.user.set_password(password)
        self.user.save()
        return {"detail": "Password reset successful."}
    
class EditProfileSerializer(serializers.ModelSerializer):
    """
    Allows a user to edit ONLY their profile fields:
    - first_name
    - last_name
    - bio
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "bio"]


class BanUserSerializer(serializers.Serializer):
    """Serializer that handles user ban. Both temporary abd permanent ban"""

    user_id = serializers.UUIDField()
    days = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        request_user = self.context["request"].user
        target_user = User.objects.filter(id=attrs["user_id"]).first()

        if not target_user:
            raise serializers.ValidationError("User does not exist.")
        # Superadmin can ban anyone
        if request_user.is_superuser:
            self.target_user = target_user
            return attrs

        # Admin rules
        if request_user.groups.filter(name="admin").exists():
            target_groups = set(target_user.groups.values_list("name", flat=True))

            if "admin" in target_groups or target_user.is_superuser:
                raise serializers.ValidationError(
                    "Admins cannot ban admins or superadmins."
                )

            self.target_user = target_user
            return attrs
        raise serializers.ValidationError("You do not have permission to ban users.")
    
    def save(self):
        days = self.validated_data.get("days")
        now = timezone.now()

        if days:
            expires_at = now + timedelta(days=days)
        else:
            expires_at = None  # permanent ban

        # Remove existing active ban (if any)
        BannedUser.objects.filter(
            user=self.target_user,
            expires_at__isnull=True
        ).delete()

        BannedUser.objects.filter(
            user=self.target_user,
            expires_at__gt=now
        ).delete()

        return BannedUser.objects.create(
            user=self.target_user,
            expires_at=expires_at
        )

class UnbanUserSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


    def validate(self, attrs):
        request_user = self.context["request"].user
        target_user = User.objects.filter(id=attrs["user_id"]).first()

        if not target_user:
            raise serializers.ValidationError("User does not exist.")
        now = timezone.now()

        active_ban = BannedUser.objects.filter(
            user=target_user
        ).filter(
            expires_at__isnull=True
        ).first() or BannedUser.objects.filter(
            user=target_user,
            expires_at__gt=now
        ).first()

        if not active_ban:
            raise serializers.ValidationError("User is not currently banned.")
        
        # Superadmin can unban anyone
        if request_user.is_superuser:
            self.active_ban = active_ban
            return attrs
        
        # Admin logic
        if request_user.groups.filter(name="admin").exists():
            target_groups = set(target_user.groups.values_list("name", flat=True))

            if "admin" in target_groups or target_user.is_superuser:
                raise serializers.ValidationError(
                    "Admins cannot unban admins or superadmins."
                )

            self.active_ban = active_ban
            return attrs
        raise serializers.ValidationError("You do not have permission to unban users.")
    

    def save(self):
        self.active_ban.delete()


class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "roles",
            "bio",
        ]
    def get_roles(self, obj):
        return list(obj.role.values_list("name", flat=True))


class RoleUpgradeRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleUpgradeRequest
        fields = ["requested_role"]

    def validate_requested_role(self, value):
        user = self.context["request"].user

        if value not in ["buyer", "seller"]:
            raise serializers.ValidationError("Invalid role request.")

        if user.groups.filter(name=value).exists():
            raise serializers.ValidationError("You already have this role.")

        return value

    def create(self, validated_data):
        user = self.context["request"].user

        return RoleUpgradeRequest.objects.create(
            user=user,
            requested_role=validated_data["requested_role"]
        )


class RoleUpgradeRequestReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])




class GrantAdminSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        try:
            return KatakaraUser.objects.get(id=value)
        except KatakaraUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
