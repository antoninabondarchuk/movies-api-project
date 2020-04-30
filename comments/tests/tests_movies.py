from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from movies.models import Film, Genre, Tv, TvGenre
from users.models import User
from people.models import Person
import factory
from faker import Factory
from myproject.settings import REST_FRAMEWORK
from rest_framework_jwt.test import APIJWTClient

faker = Factory.create()


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre


class TvGenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TvGenre


class FilmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Film

    vote_average = 0.
    vote_count = 0

    @factory.post_generation
    def genre_ids(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for genre_id in extracted:
                self.genre_ids.add(genre_id)


class TvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tv

    @factory.post_generation
    def genre_ids(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for genre_id in extracted:
                self.genre_ids.add(genre_id)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = faker.email()
    is_active = True


class PeopleFactory(factory.django.DjangoModelFactory):
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


class FilmsJsonViewTests(APITestCase):
    client_class = APIJWTClient

    def set_logined_user(self):
        get_token_url = reverse('token_obtain_pair')
        response = self.client.post(get_token_url,
                                    data={'username': self.user.username, 'password': 'pass'},
                                    format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'{token}')

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('pass')
        self.user.save()

        self.genres = GenreFactory.create_batch(3)
        self.films = FilmFactory.create_batch(21, genre_ids=self.genres)
        self.films.sort(key=lambda x: x.id)

        self.url = reverse('movies:movies_json')
        self.set_logined_user()

    def test_positive_get(self):

        expected_result = {
            "count": 21,
            "next": "http://testserver/movies/api/?page=2",
            "previous": None,
            "results": [{
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
                for film in self.films[:REST_FRAMEWORK['PAGE_SIZE']]
            ]
        }

        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(response_json, expected_result)

    def test_positive_put_film(self):
        input_data = {
            'film': {
                'id': str(self.films[0].id)
            },
            'vote': 10.0
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, input_data)

    def test_null_film_id_put(self):
        input_data = {
            'film': {
                'id': ''
            },
            'vote': 10.0
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, 'Such movie does not exist!')

    def test_null_tv_id_put(self):
        input_data = {
            'tv': {
                'id': ''
            },
            'vote': 10.0
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, 'Such movie does not exist!')

    def test_null_data_put(self):
        input_data = {}
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, 'Such movie does not exist!')

    def test_null_vote_put(self):
        input_data = {
            'film': {
                'id': str(self.films[0].id)
            },
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'vote': ['This field is required.']})

    def test_only_vote_put(self):
        input_data = {
            'vote': 10.0
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, 'Such movie does not exist!')

    def test_unauthenticated_put_film(self):
        self.client.credentials()
        response = self.client.put(self.url, format='json', data={'film': {'id': str(self.films[0].id)}, 'vote': 0})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FilmWithPersonJsonViewTests(APITestCase):
    client_class = APIJWTClient

    def setUp(self):
        self.genres = GenreFactory.create_batch(3)
        self.films = FilmFactory.create_batch(21, genre_ids=self.genres)
        self.films.sort(key=lambda x: x.id)
        self.actor_name = 'Monica Bellucci'
        self.actor = PeopleFactory(known_for=self.films, name=self.actor_name)
        self.url = '/movies/api/with_actor/?actor_name=Monica%20Bellucci'

    def test_positive_get(self):
        expected_result = {
            "count": 21,
            "next": "http://testserver/movies/api/with_actor/?actor_name=Monica+Bellucci&page=2",
            "previous": None,
            "results": [{
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
                for film in self.films[:REST_FRAMEWORK['PAGE_SIZE']]
            ]
        }

        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(response_json, expected_result)

    def test_null_data(self):
        self.url = reverse('movies:films_with_person_json')
        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'actor_name': ['This field may not be null.']})
