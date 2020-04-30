from django.shortcuts import render
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator
from movies.permissions import IsUserOrReadOnly
from .serializers import VoteSerializer, ActorNameSerializer
from .models import Film, Tv
from rest_framework.pagination import PageNumberPagination

SHARED_TITLES = ("id", "source_id", "popularity", "vote_average",
                 "vote_count", "poster_path", "backdrop_path",
                 "original_language", "type", "overview")
FILM_TITLES = SHARED_TITLES + ("title", "original_title", "release_date")
TV_TITLES = SHARED_TITLES + ("name", "original_name", "first_air_date")
ACTOR_NAME_FIELD = openapi.Parameter('actor_name', openapi.IN_QUERY, type=openapi.TYPE_STRING)
PAGE_FIELD = openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


class FilmsView(View):
    def get(self, request):
        films_list = Film.objects.all()
        tvs_list = Tv.objects.all()
        union_films = films_list.values(*FILM_TITLES).union(tvs_list.values(*TV_TITLES))

        paginator = Paginator(union_films, 20)  # Show 20 films per page
        page = request.GET.get('page')
        all_films = paginator.get_page(page)
        for film in all_films:
            film['genres'] = []
            if film['type'] == 'movie':
                current_film = Film.objects.get(source_id=film['source_id'])
                current_genres = current_film.genre_ids.all()
            else:
                current_film = Tv.objects.get(source_id=film['source_id'])
                current_genres = current_film.genre_ids.all()
            for genre_obj in current_genres:
                genre = dict(id=genre_obj.source_id, title=genre_obj.title)
                film['genres'].append(genre)
        return render(request, 'films.html', {'films': all_films})


class FilmsWithView(View):
    def get(self, request, actor_name):
        films_with = Film.objects.filter(
            person__name__icontains=actor_name.replace("_", " "))
        tv_with = Tv.objects.filter(
            person__name__icontains=actor_name.replace("_", " "))
        all_with = films_with.values(*FILM_TITLES).union(tv_with.values(*TV_TITLES)).order_by('source_id')
        paginator = Paginator(all_with, 20)  # Show 20 films per page
        page = request.GET.get('page')
        films = paginator.get_page(page)
        for film in films:
            film['genres'] = []
            if film['type'] == 'movie':
                current_film = Film.objects.get(source_id=film['source_id'])
                current_genres = current_film.genre_ids.all()
            else:
                current_film = Tv.objects.get(source_id=film['source_id'])
                current_genres = current_film.genre_ids.all()
            for genre_obj in current_genres:
                genre = dict(id=genre_obj.source_id, title=genre_obj.title)
                film['genres'].append(genre)
        return render(request, 'films_with.html', {'films': films})


class FilmsJsonView(APIView):
    """
    Implements the ability to interact with whole list of films and tvs.
    """
    permission_classes = (IsUserOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    @swagger_auto_schema(manual_parameters=[PAGE_FIELD])
    def get(self, request):
        """
        To reply to users and guests with whole paginated serialized list of union of films and tvs.
        :param request: HTTP get request [with 'page' param].
        :return: HTTP response. With JSON data of films and tvs, Http status 200
                 or serializer validation's errors with messages and Http status 400.
        """
        films_list = Film.objects.all()
        tvs_list = Tv.objects.all()
        union_films = films_list.values(*FILM_TITLES).union(tvs_list.values(*TV_TITLES)).order_by('id')
        paginator = self.pagination_class()
        result = paginator.paginate_queryset(union_films, request)
        paginated_response = paginator.get_paginated_response(result)
        return paginated_response

    @swagger_auto_schema(request_body=VoteSerializer)
    def put(self, request):
        """
        To allow users to vote for films and tvs.
        :param request: HTTP request with info about film and user's vote in the data attr.
        :return: HTTP response. With JSON data of films and tvs, Http status 200
                 or serializer validation's errors with messages and Http status 400.
        """
        movie = VoteSerializer.get_film_or_tv(request.data)
        if not movie:
            return Response(data='Such movie does not exist!', status=status.HTTP_404_NOT_FOUND)
        film_data_serializer = VoteSerializer(instance=movie, data=request.data)
        if film_data_serializer.is_valid():
            film_data_serializer.update(instance=movie, validated_data=film_data_serializer.validated_data)
            return Response(film_data_serializer.validated_data, status=status.HTTP_200_OK)
        return Response(film_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilmsWithPersonJsonView(APIView):
    """
    Enable users to search films and tvs by the actor's or director's name.
    """
    permission_classes = (IsUserOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )

    @swagger_auto_schema(manual_parameters=[ACTOR_NAME_FIELD, PAGE_FIELD])
    def get(self, request):
        """
        To the GET request from users or guests
        to discover serialized paginated list of films and tvs
        which contain actor's or director's name, assigned by the user or guest.
        :param request: HTTP request data [with 'page' [and/or 'actor_name'] param(s)].
        :return: HTTP response. With JSON data of films and tvs
                 which contain actor's or director's name, Http status code 200
                 or serializer validation's errors with messages and Http status 400.
         """
        actor_name_serializer = ActorNameSerializer({'actor_name': request.GET.get('actor_name')},
                                                    data={'actor_name': request.GET.get('actor_name')})
        if actor_name_serializer.is_valid():
            films_with = Film.objects.filter(
                person__name__icontains=actor_name_serializer.validated_data['actor_name'])
            tv_with = Tv.objects.filter(
                person__name__icontains=actor_name_serializer.validated_data['actor_name'])
            all_with = films_with.values(*FILM_TITLES).union(tv_with.values(*TV_TITLES)).order_by('id')
            paginator = self.pagination_class()
            result = paginator.paginate_queryset(all_with, request)
            paginated_response = paginator.get_paginated_response(result)
            return paginated_response
        return Response(actor_name_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
