from rest_framework.permissions import BasePermission

class RoleExclusivityPermission(BasePermission):
    """
    Enforces:
    - superadmin is exclusive
    - admin is exclusive
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superadmin: absolute authority
        if user.is_superuser:
            return True

        group_names = set(user.groups.values_list("name", flat=True))

        # Admin must not mix roles
        if "admin" in group_names and len(group_names) > 1:
            return False

        return True

class IsBuyer(BasePermission):
    """
    Allows access to buyers.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name="buyer").exists()

class IsSeller(BasePermission):
    """
    Allows access to sellers.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name="seller").exists()

class IsAdmin(BasePermission):
    """
    Allows access to admins only.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name="admin").exists()

class IsSuperAdmin(BasePermission):
    """
    Allows access to superadmin only.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )

class IsBuyerOrSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name__in=["buyer", "seller"]).exists()
