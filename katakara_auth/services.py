from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from .models import BannedUser


class BanAwareJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        now = timezone.now()
        active_ban = BannedUser.objects.filter(
            user=user
        ).filter(
            expires_at__isnull=True
        ).first() or BannedUser.objects.filter(
            user=user,
            expires_at__gt=now
        ).first()

        if active_ban:
            raise AuthenticationFailed("Your account has been banned.")

        return user
