from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from movies.models import Film, Tv
from users import utils
from users.permissions import JWTAuthentication, NonLogined
from .serializers import UserAccountSerializer, DeleteManyFilmTvSerializer


class CreateUserView(APIView):
    """
    To create new users.
    """
    permission_classes = (NonLogined, )

    @swagger_auto_schema(request_body=UserAccountSerializer)
    def post(self, request):
        """
        To serialize and create UserAccount with JSON data from request.
        :param request: HTTP request with data for UserAccount creation: username and password.
        :return: HTTP response. With serialized JSON data of new user account and Http status code 200
                 or serializer validation's errors with messages and Http status 400.
        """
        user_serializer = UserAccountSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishListView(APIView):
    """
    For describing wish lists to the certain user,
    for addind and removing films and tvs from it.
    """
    permission_classes = (JWTAuthentication,)

    def get(self, request):
        """
        To check if exists and serialize user account to describe whole user's wish lists of films and tvs.
        :param request: HTTP request with user and his params inside .data.
        :return: HTTP response with UserAccountSerializer data and status code 200.
        """
        wish_list = utils.get_user_account(request.user.id)
        if wish_list is None:
            return Response('User with such id does not exist.', status=status.HTTP_404_NOT_FOUND)
        wish_list_serializer = UserAccountSerializer(wish_list)
        return Response(wish_list_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserAccountSerializer)
    def put(self, request):
        """
        To add new films and tvs to the user's wish lists.
        :param request: HTTP request with user and his wish lists inside .data.
        :return: HTTP response. With serialized JSON data of updated user account and Http status code 200
                 or serializer validation's errors with messages and Http status 400.
        """
        user_wish_list = utils.get_user_account(request.user.id)
        if user_wish_list is None:
            return Response('User with such id does not exist.', status=status.HTTP_404_NOT_FOUND)
        wish_list_serializer = UserAccountSerializer(instance=user_wish_list, data=request.data, partial=True)
        if wish_list_serializer.is_valid():
            wish_list_serializer.update(instance=user_wish_list, validated_data=wish_list_serializer.validated_data)
            return Response(wish_list_serializer.data, status=status.HTTP_200_OK)
        return Response(wish_list_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=DeleteManyFilmTvSerializer)
    def delete(self, request):
        """
        The function which implements DELETE http method t remove tvs and films from their wish lists of user.
        :param request: HTTP request with user and his wish lists inside .data.
        :return: HTTP response with status code 204.
        """
        user_account = utils.get_user_account(request.user.id)
        films_data_serializer = DeleteManyFilmTvSerializer(data=request.data)
        if films_data_serializer.is_valid():
            for film in films_data_serializer.data.get('films_ids', []):
                film_instance_to_delete = get_object_or_404(Film, id=film['id'])
                user_account.wish_list.remove(film_instance_to_delete)
            for tv in films_data_serializer.data.get('tvs_ids', []):
                tv_instance_to_delete = get_object_or_404(Tv, id=tv['id'])
                user_account.wish_list_tv.remove(tv_instance_to_delete)
            user_account.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(films_data_serializer.errors, status.HTTP_400_BAD_REQUEST)
