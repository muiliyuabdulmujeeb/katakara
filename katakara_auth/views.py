from django.shortcuts import get_object_or_404, render
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.models import Group
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RoleUpgradeRequest, KatakaraUser, Role
from .serializers import BanUserSerializer, EditProfileSerializer, ForgotPasswordSerializer, GrantAdminSerializer, ResetPasswordSerializer, RoleUpgradeRequestCreateSerializer, RoleUpgradeRequestReviewSerializer, SignupSerializer, LogoutSerializer, CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, UnbanUserSerializer, UserProfileSerializer
from .permissions import IsAdmin, IsSuperAdmin


# Create your views here.

#login
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

#signup
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
            },
            status=status.HTTP_201_CREATED
        )


#logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

#refresh tokens
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


#forgot password
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            {"detail": "Password reset link sent.", "data": data},
            status=status.HTTP_200_OK
        )


#reset password (second step after forgot password above)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)

#edit profile    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = EditProfileSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

#ban user
class BanUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BanUserSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User banned successfully."},
            status=status.HTTP_200_OK
        )


#unban user
class UnbanUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UnbanUserSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User unbanned successfully."},
            status=status.HTTP_200_OK
        )


    
class RequestRoleUpgradeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoleUpgradeRequestCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Role upgrade request submitted."},
            status=201
        )

class PendingRoleUpgradeRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        qs = RoleUpgradeRequest.objects.filter(status="pending")
        serializer = RoleUpgradeRequestReviewSerializer(qs, many=True)
        return Response(serializer.data)

class ReviewRoleUpgradeRequestView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        role_request = get_object_or_404(RoleUpgradeRequest, pk=pk, status="pending")
        serializer = RoleUpgradeRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        if action == "approve":
            group = Group.objects.get(name=role_request.requested_role)
            role_request.user.groups.add(group)
            role_request.status = "approved"
        else:
            role_request.status = "rejected"
        role_request.reviewed_by = request.user
        role_request.reviewed_at = timezone.now()
        role_request.save()

        return Response({"detail": "Request processed successfully."})


class CancelRoleUpgradeRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        role_request = get_object_or_404( RoleUpgradeRequest, pk=pk, user=request.user, status="pending")

        role_request.delete()

        return Response(
            {"detail": "Role upgrade request cancelled."},
            status=status.HTTP_204_NO_CONTENT
        )


class SuperAdminGrantAdminView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        print("step 1")
        serializer = GrantAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print("step 2")
        user = serializer.validated_data["user_id"]

        if user == request.user:
            return Response(
                {"detail": "You cannot modify your own roles."},
                status=status.HTTP_400_BAD_REQUEST
            )

        print("Step 3")
        admin_role, _ = Role.objects.get_or_create(name="admin")
        admin_group = Group.objects.get(name="admin")

        print("step 4")
        try:
            with transaction.atomic():
                user.role.set([admin_role])
                user.groups.set([admin_group])
        except IntegrityError as e:
            raise Exception(f"ROLE ASSIGNMENT FAILED: {e}")


        print("step 5")
        return Response(
            {"detail": f"All previous roles revoked. User {user.email} is now an admin."},
            status=status.HTTP_200_OK
        )
