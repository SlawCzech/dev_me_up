from rest_framework.permissions import BasePermission


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admins to retrieve any user
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Allow users to retrieve their own information
        return obj == request.user
