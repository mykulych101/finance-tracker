from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    """Authenticated users who confirmed their email.

    Registration hands out JWT tokens before the activation link is opened,
    so `IsAuthenticated` alone does not keep unverified users out.
    """

    message = "Email is not verified."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)
