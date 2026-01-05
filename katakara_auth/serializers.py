from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import Token, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


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
    
class SignSerializer(serializers.ModelSerializer):
    """Sign up serializer responsible for validating input, safey creating user and assigning allowed roles (buyer and seller in this case)"""

    password = serializers.CharField(write_only= True)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=["buyer", "seller"]),
        required=False
    )

    class Meta:
        model = User
        fields = ["email", "password", "roles"]

    def validate_roles(self, value):
        if not value:
            return ["buyer"]

        unique_roles = set(value)

        if "buyer" in unique_roles or "seller" in unique_roles:
            return list(unique_roles)

        raise serializers.ValidationError("Invalid role selection.")
    
    def create(self, validated_data):
        roles = validated_data.pop("roles", ["buyer"])
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        allowed_groups = Group.objects.filter(name__in=roles)
        user.groups.set(allowed_groups)

        return user

class LogoutSerializer(serializers.Serializer):
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
