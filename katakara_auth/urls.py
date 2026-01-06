from django.urls import path

from .views import CancelRoleUpgradeRequestView, LoginView, PendingRoleUpgradeRequestsView, RequestRoleUpgradeView, ReviewRoleUpgradeRequestView, SignupView, LogoutView, TokenRefreshView, ForgotPasswordView, ResetPasswordView, UserProfileView, BanUserView, UnbanUserView


urlpatterns = [
    # Authentication
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),  
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    # User profile
    path("users/me/profile/", UserProfileView.as_view(), name="profile"), 

    # Admin / Moderation
    path("admin/users/ban/", BanUserView.as_view(), name="ban-user"),
    path("admin/users/unban/", UnbanUserView.as_view(), name="unban-user"),

    #roles
    path("roles/request/", RequestRoleUpgradeView.as_view()),
    path("roles/requests/", PendingRoleUpgradeRequestsView.as_view()),
    path("roles/requests/<uuid:pk>/review/", ReviewRoleUpgradeRequestView.as_view()),
    path("roles/requests/<uuid:pk>/cancel/", CancelRoleUpgradeRequestView.as_view()),
]
