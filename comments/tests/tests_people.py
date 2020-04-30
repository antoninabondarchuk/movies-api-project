import factory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.test import APIJWTClient

from myproject.settings import REST_FRAMEWORK
from people.models import Person
from tests.tests_movies import GenreFactory, TvGenreFactory, FilmFactory, TvFactory


class PeopleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Person

    @factory.post_generation
    def known_for(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for film in extracted:
                self.known_for.add(film)

    @factory.post_generation
    def known_for_tv(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for film in extracted:
                self.known_for_tv.add(film)


class FilmWithPersonJsonViewTests(APITestCase):
    client_class = APIJWTClient

    def setUp(self):
        self.genres = GenreFactory.create_batch(3)
        self.tv_genres = TvGenreFactory.create_batch(3)
        self.films = FilmFactory.create_batch(1, genre_ids=self.genres, title='Finding Nemo')
        self.films.sort(key=lambda x: x.id)
        self.tvs = TvFactory.create_batch(3, genre_ids=self.tv_genres, name='Finding Nemo')
        self.tvs.sort(key=lambda x: x.id)
        self.actors = PeopleFactory.create_batch(21, known_for=self.films, known_for_tv=self.tvs)
        self.actors.sort(key=lambda x: x.id)
        self.url = '/actors/api/'

    def test_positive_get(self):
        self.url += '?film_title=finding_nemo'

        expected_result = {
            "count": 21,
            "next": "http://testserver/actors/api/?film_title=finding_nemo&page=2",
            "previous": None,
            "results": [
                {
                    "id": str(actor.id),
                    "popularity": actor.popularity,
                    "gender": actor.gender,
                    "profile_path": actor.profile_path,
                    "adult": actor.adult,
                    "name": actor.name,
                    "source_id": actor.source_id,
                    "known_for": [
                        {
                            "id": str(film.id),
                            "source_id": film.source_id,
                            "popularity": film.popularity,
                            "vote_average": film.vote_average,
                            "vote_count": film.vote_count,
                            "poster_path": film.poster_path,
                            "backdrop_path": film.backdrop_path,
                            "original_language": film.original_language,
                            "type": film.type,
                            "overview": film.overview,
                            "title": film.title,
                            "original_title": film.original_title,
                            "release_date": film.release_date
                        }
                        for film in actor.known_for.all().order_by('id')
                    ],
                    "known_for_tv": [
                        {
                            "id": str(tv.id),
                            "source_id": tv.source_id,
                            "popularity": tv.popularity,
                            "vote_average": tv.vote_average,
                            "vote_count": tv.vote_count,
                            "poster_path": tv.poster_path,
                            "backdrop_path": tv.backdrop_path,
                            "original_language": tv.original_language,
                            "type": tv.type,
                            "overview": tv.overview,
                            "name": tv.name,
                            "original_name": tv.original_name,
                            "first_air_date": tv.first_air_date
                        }
                        for tv in actor.known_for_tv.all().order_by('id')
                    ]
                }
                for actor in self.actors[:REST_FRAMEWORK['PAGE_SIZE']]
            ]
        }

        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(response_json, expected_result)

    def test_null_data(self):
        self.url = reverse('people:actors_in_film_json')
        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'film_title': ['This field may not be null.']})
