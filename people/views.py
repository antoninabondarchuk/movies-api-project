from django.core.paginator import Paginator
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PersonSerializer, FilmTitleSerializer
from .models import Person
from django.views import View

FILM_TITLE_FIELD = openapi.Parameter('film_title', openapi.IN_QUERY, type=openapi.TYPE_STRING)
PAGE_FIELD = openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


class ActorsInView(View):
    def get(self, request, film_title):
        actors = Person.objects.filter(
            known_for__original_title__icontains=film_title.replace("_", " ")) | \
            Person.objects.filter(
                known_for__title__icontains=film_title.replace("_", " ")) \
            .order_by('source_id')
        paginator = Paginator(actors, 20)  # Show 20 films per page
        page = request.GET.get('page')
        actors_paginated = paginator.get_page(page)
        return render(request, 'actors_in.html', {'actors': actors_paginated})


class PeopleInFilmJsonView(APIView):
    """
    Implements the ability to search for a list with actors and directors
    according to the assigned film or tv title by the user or guest.
    """

    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    @swagger_auto_schema(manual_parameters=[FILM_TITLE_FIELD, PAGE_FIELD])
    def get(self, request):
        """
        Implements the ability to discover serialized paginated list of actors and directors
        which contain film's or tv's title, assigned by the user or guest.
        :param request: HTTP request data [with 'page' [and/or 'film_title'] param(s)].
        :return: HTTP response with JSON data of list of actors and directors,
                 who are known for accepted film or tv title with status code 200
                 or serializer validation's errors with messages and Http status 400.
        """
        film_title_serializer = FilmTitleSerializer({'film_title': request.GET.get('film_title')},
                                                    data={'film_title': request.GET.get('film_title')})
        if film_title_serializer.is_valid():
            people = Person.objects.filter(
                known_for__original_title__icontains=film_title_serializer.validated_data['film_title']) | \
                Person.objects.filter(
                known_for__title__icontains=film_title_serializer.validated_data['film_title']) \
                .order_by('id')
            paginator = self.pagination_class()
            result = paginator.paginate_queryset(people, request)
            serializer_person = PersonSerializer(result, many=True, read_only=True)
            paginated_response = paginator.get_paginated_response(serializer_person.data)
            return paginated_response
        return Response(film_title_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
