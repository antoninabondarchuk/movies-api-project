from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from comments.models import Comment
from comments.serializers import CommentSerializer, MovieSerializer, RootCommentSerializer, DeleteCommentSerializer
from movies.permissions import IsUserOrReadOnly

MOVIE_ID_FIELD = openapi.Parameter('movie_id', openapi.IN_QUERY, type=openapi.FORMAT_UUID)
MOVIE_TYPE_FIELD = openapi.Parameter('movie_type', openapi.IN_QUERY, type=openapi.TYPE_STRING)
PAGE_FIELD = openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


class MovieCommentsView(APIView):
    """
    Viewing and adding comments (only for users) to the film or tv.
    """
    permission_classes = (IsUserOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )

    @swagger_auto_schema(manual_parameters=[MOVIE_ID_FIELD, MOVIE_TYPE_FIELD, PAGE_FIELD, ])
    def get(self, request):
        """
        Displaying comments tree of the film or tv.
        :param request: HTTP request with 'page', 'movie_id' and 'movie_type' in headers.
        :return: HTTP response. With JSON data of film or tv and comments, Http status 200
                 or serializer validation's errors with messages and Http status 400.
        """
        request_headers_info = {'movie_id': request.GET.get('movie_id'),
                                'movie_type': request.GET.get('movie_type')}
        movie_serializer = MovieSerializer(request_headers_info, data=request_headers_info)
        if movie_serializer.is_valid():
            movie = MovieSerializer.get_movie(movie_serializer.validated_data)
            if movie is None:
                return Response('No such film or tv.', status=status.HTTP_404_NOT_FOUND)
            root_comments = Comment.get_root_nodes().filter(
                (Q(film__type=movie.type) & Q(film_id=movie.id)) |
                (Q(tv__type=movie.type) & Q(tv_id=movie.id))).order_by('-created_date')
            paginator = self.pagination_class()
            result = paginator.paginate_queryset(root_comments, request)
            user_comment_serializer = RootCommentSerializer(result, many=True)
            paginated_response = paginator.get_paginated_response(user_comment_serializer.data)
            return paginated_response
        return Response(data=movie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request):
        """
        Adding new comments for users.
        :param request: HTTP request with user and his comment info inside .data.
        :return: HTTP response. With serialized JSON data of updated comments tree and Http status code 201
                 or serializer validation's errors with messages and Http status 400.
        """
        comment_serializer = CommentSerializer(data=request.data, context={'request': request})
        if comment_serializer.is_valid(raise_exception=True):
            comment_serializer.save()
            return Response(data=comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=DeleteCommentSerializer)
    def delete(self, request):
        """
        Allows authors delete their comments.
        :param request: HTTP request with user and id comment info inside .data.
        :return: HTTP response with status code 204 or 404 if requested comment does not exist.
        """
        comment_serializer = DeleteCommentSerializer(request.data, data=request.data)
        if comment_serializer.is_valid():
            try:
                comment_to_delete = Comment.objects.get(
                    id=comment_serializer.validated_data.get('id'), author=request.user.id)
                comment_to_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Comment.DoesNotExist:
                return Response('Sorry, no comment with such id.', status=status.HTTP_404_NOT_FOUND)
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
