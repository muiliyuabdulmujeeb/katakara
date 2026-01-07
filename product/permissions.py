from rest_framework.permissions import BasePermission



class IsSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return False  # superadmin does not sell

        return user.groups.filter(name="seller").exists()


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(name="admin").exists()

class IsProductOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
























""" class CanCreateProduct(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return (
            user.groups.filter(name="seller").exists()
            and user.has_perm("products.create_product")
        )

class CanModifyOwnProduct(BasePermission):

    # Seller can modify only products they own. Admin cannot.

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if not user.groups.filter(name="seller").exists():
            return False

        if not user.has_perm("products.update_own_product"):
            return False

        return obj.owner == user

class CanBuyProduct(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return (
            user.groups.filter(name="buyer").exists()
            and user.has_perm("products.buy_product")
        )
 """


