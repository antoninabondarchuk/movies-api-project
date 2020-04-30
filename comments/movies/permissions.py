from django.http import Http404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User
from users.tokens import MyToken


class IsUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow users to edit votes.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        try:
            token = MyToken(token=request.headers['Authorization'])
        except (KeyError, TokenError):
            return False
        try:
            request.user = User.objects.get(id=token.payload['user_id'])
        except User.DoesNotExist:
            raise Http404('User with such token does not exist or expired.')
        return True
