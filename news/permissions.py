from django.http import Http404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User
from users.tokens import MyToken


class IsSuperUser(permissions.BasePermission):
    """
    Checks is the user is superuser.
    """

    def has_permission(self, request, view):
        """
        Checks and gives the rights only to superusers.
        :param request: the HTTP request with data about user.
        :param view: current view.
        :return: True if user is a superuser, Http response with status code 404 and error message.
        """
        try:
            token = MyToken(token=request.headers['Authorization'])
        except (KeyError, TokenError):
            return False
        try:
            request.user = User.objects.get(id=token.payload['user_id'])
            if request.user.is_superuser:
                return True
            message = 'You have to be a superuser to create news.'
            raise PermissionDenied(detail=message)
        except User.DoesNotExist:
            raise Http404('User with such token does not exist or expired.')
