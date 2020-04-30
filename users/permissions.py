from django.http import Http404
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User
from users.tokens import MyToken


class JWTAuthentication(BasePermission):
    """
    Implements custom Json Web Token Authentication.
    """
    def has_permission(self, request, view):
        """
        Checks guest's ability to authenticate as user by getting a token.
        :param request: request data with headers to check.
        :param view: just a current view for authentication.
        :return: True, if user was successfully authenticate with token
                 or Http404 Error with description message.
        """
        try:
            token = MyToken(token=request.headers['Authorization'])
        except (KeyError, TokenError):
            return False
        try:
            request.user = User.objects.get(id=token.payload['user_id'])
        except User.DoesNotExist:
            raise Http404('User with such token does not exist or expired.')
        return True


class NonLogined(BasePermission):
    """
    Checking for creating users only by unauthorized users (guests).
    """
    def has_permission(self, request, view):
        """
        Gives permission for guests? not for users.
        """
        try:
            token = MyToken(token=request.headers['Authorization'])
        except (KeyError, TokenError):
            return True
        try:
            request.user = User.objects.get(id=token.payload['user_id'])
        except (User.DoesNotExist, KeyError):
            return True
        message = 'Please, log out to create new account.'
        raise PermissionDenied(detail=message)
