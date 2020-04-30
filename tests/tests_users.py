from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.test import APIJWTClient
from tests.tests_movies import UserFactory, GenreFactory, FilmFactory, TvGenreFactory, TvFactory
import factory
from users.models import UserAccount


class UserAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserAccount

    @factory.post_generation
    def wish_list(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for film in extracted:
                self.wish_list.add(film)

    @factory.post_generation
    def wish_list_tv(self, create, extracted):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for tv in extracted:
                self.wish_list_tv.add(tv)


class CreateUserViewTests(APITestCase):
    client_class = APIJWTClient

    def set_logined_user(self):
        get_token_url = reverse('token_obtain_pair')
        response = self.client.post(get_token_url,
                                    data={'username': self.user.username, 'password': 'password'},
                                    format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'{token}')

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('password')
        self.user.save()
        self.url = reverse('users:create_user')

    def test_positive_create_user(self):
        input_data = {
            'user': {
                'username': 'username',
                'password': 'password',
                'email': 'email@example.com'
            }
        }
        expected_result = {
            'user': {
                'username': 'username',
                'email': 'email@example.com'
            },
            "wish_list": [],
            "wish_list_tv": []
        }
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        response_json.pop('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json, expected_result)

    def test_logined_create_user(self):
        input_data = {
            'user': {
                'username': 'username',
                'password': 'password',
                'email': 'email@example.com'
            }
        }
        self.set_logined_user()
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_json, {'detail': 'Please, log out to create new account.'})

    def test_user_exists_create(self):
        input_data = {
            'user': {
                'username': self.user.username,
                'password': 'password',
                'email': self.user.email
            }
        }
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {"user": {"username": ["A user with that username already exists."]}})

    def test_null_data_create_user(self):
        input_data = {}
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'user': ['This field is required.']})


class WishListViewTests(APITestCase):
    client_class = APIJWTClient

    def set_logined_user(self):
        get_token_url = reverse('token_obtain_pair')
        response = self.client.post(get_token_url,
                                    data={'username': self.user.username, 'password': 'pass'},
                                    format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'{token}')

    def setUp(self):
        self.url = reverse('users:wish_list')
        self.user = UserFactory()
        self.user.set_password('pass')
        self.user.save()
        self.set_logined_user()

        self.genres = GenreFactory.create_batch(2)
        self.films = FilmFactory.create_batch(2, genre_ids=self.genres)
        self.films.sort(key=lambda x: x.id)

        self.tv_genres = TvGenreFactory.create_batch(2)
        self.tvs = TvFactory.create_batch(2, genre_ids=self.tv_genres)
        self.tvs.sort(key=lambda x: x.id)

        self.new_film = FilmFactory(genre_ids=self.genres)
        self.new_tv = TvFactory(genre_ids=self.tv_genres)

        self.user_account = UserAccountFactory(user=self.user, wish_list=self.films, wish_list_tv=self.tvs)

    def test_positive_get(self):
        expected_result = {
            'id': str(self.user_account.id),
            'user':
                {
                    'username': self.user_account.user.username,
                    'email': self.user_account.user.email
            },
            'wish_list': [
                {
                    'id': str(film.id),
                    'source_id': film.source_id,
                    'popularity': film.popularity,
                    'vote_average': film.vote_average,
                    'vote_count': film.vote_count,
                    'poster_path': film.poster_path,
                    'backdrop_path': film.backdrop_path,
                    'original_language': film.original_language,
                    'type': film.type,
                    'overview': film.overview,
                    'title': film.title,
                    'original_title': film.original_title,
                    'release_date': film.release_date
                }
                for film in self.user_account.wish_list.all()
            ],
            'wish_list_tv': [
                {
                    'id': str(tv.id),
                    'source_id': tv.source_id,
                    'popularity': tv.popularity,
                    'vote_average': tv.vote_average,
                    'vote_count': tv.vote_count,
                    'poster_path': tv.poster_path,
                    'backdrop_path': tv.backdrop_path,
                    'original_language': tv.original_language,
                    'type': tv.type,
                    'overview': tv.overview,
                    'name': tv.name,
                    'original_name': tv.original_name,
                    'first_air_date': tv.first_air_date
                }
                for tv in self.user_account.wish_list_tv.all()
            ]
        }
        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_result)

    def test_unauthorized(self):
        self.client.credentials()

        response_get = self.client.get(self.url, format='json')
        response_get_json = response_get.json()
        self.assertEqual(response_get.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_get_json, {'detail': 'Authentication credentials were not provided.'})

        response_put = self.client.put(self.url, format='json', data={})
        response_put_json = response_put.json()
        self.assertEqual(response_put.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_put_json, {'detail': 'Authentication credentials were not provided.'})

        response_delete = self.client.delete(self.url, format='json', data={})
        response_delete_json = response_delete.json()
        self.assertEqual(response_delete.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_delete_json, {'detail': 'Authentication credentials were not provided.'})

    def test_positive_put(self):
        input_data = {
            'wish_list': [
                {
                    'id': str(self.new_film.id)
                }
            ],
            'wish_list_tv': [
                {
                    'id': str(self.new_tv.id)
                }
            ]

        }
        expected_result = {
            'id': str(self.user_account.id),
            'user':
                {
                    'username': self.user_account.user.username,
                    'email': self.user_account.user.email
            },
            'wish_list': [
                {
                    'id': str(film.id),
                    'source_id': film.source_id,
                    'popularity': film.popularity,
                    'vote_average': film.vote_average,
                    'vote_count': film.vote_count,
                    'poster_path': film.poster_path,
                    'backdrop_path': film.backdrop_path,
                    'original_language': film.original_language,
                    'type': film.type,
                    'overview': film.overview,
                    'title': film.title,
                    'original_title': film.original_title,
                    'release_date': film.release_date
                }
                for film in self.user_account.wish_list.all()
            ] + [{
                'id': str(self.new_film.id),
                'source_id': self.new_film.source_id,
                'popularity': self.new_film.popularity,
                'vote_average': self.new_film.vote_average,
                'vote_count': self.new_film.vote_count,
                'poster_path': self.new_film.poster_path,
                'backdrop_path': self.new_film.backdrop_path,
                'original_language': self.new_film.original_language,
                'type': self.new_film.type,
                'overview': self.new_film.overview,
                'title': self.new_film.title,
                'original_title': self.new_film.original_title,
                'release_date': self.new_film.release_date
            }],
            'wish_list_tv': [
                {
                    'id': str(tv.id),
                    'source_id': tv.source_id,
                    'popularity': tv.popularity,
                    'vote_average': tv.vote_average,
                    'vote_count': tv.vote_count,
                    'poster_path': tv.poster_path,
                    'backdrop_path': tv.backdrop_path,
                    'original_language': tv.original_language,
                    'type': tv.type,
                    'overview': tv.overview,
                    'name': tv.name,
                    'original_name': tv.original_name,
                    'first_air_date': tv.first_air_date
                }
                for tv in self.user_account.wish_list_tv.all()
            ] + [{
                'id': str(self.new_tv.id),
                'source_id': self.new_tv.source_id,
                'popularity': self.new_tv.popularity,
                'vote_average': self.new_tv.vote_average,
                'vote_count': self.new_tv.vote_count,
                'poster_path': self.new_tv.poster_path,
                'backdrop_path': self.new_tv.backdrop_path,
                'original_language': self.new_tv.original_language,
                'type': self.new_tv.type,
                'overview': self.new_tv.overview,
                'name': self.new_tv.name,
                'original_name': self.new_tv.original_name,
                'first_air_date': self.new_tv.first_air_date
            }]
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_result)

    def test_wrong_user_data_put(self):
        input_data = {
            "user": {
                "username": "wrong",
                "password": "wrong",
                "email": "user@example.com"
            }
        }
        expected_result = {
            'id': str(self.user_account.id),
            'user':
                {
                    'username': self.user.username,
                    'email': self.user.email
            },
            'wish_list': [
                {
                    'id': str(film.id),
                    'source_id': film.source_id,
                    'popularity': film.popularity,
                    'vote_average': film.vote_average,
                    'vote_count': film.vote_count,
                    'poster_path': film.poster_path,
                    'backdrop_path': film.backdrop_path,
                    'original_language': film.original_language,
                    'type': film.type,
                    'overview': film.overview,
                    'title': film.title,
                    'original_title': film.original_title,
                    'release_date': film.release_date
                }
                for film in self.user_account.wish_list.all()
            ],
            'wish_list_tv': [
                {
                    'id': str(tv.id),
                    'source_id': tv.source_id,
                    'popularity': tv.popularity,
                    'vote_average': tv.vote_average,
                    'vote_count': tv.vote_count,
                    'poster_path': tv.poster_path,
                    'backdrop_path': tv.backdrop_path,
                    'original_language': tv.original_language,
                    'type': tv.type,
                    'overview': tv.overview,
                    'name': tv.name,
                    'original_name': tv.original_name,
                    'first_air_date': tv.first_air_date
                }
                for tv in self.user_account.wish_list_tv.all()
            ]
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_result)

    def test_wrong_wish_list_ids_put(self):
        input_data = {
            'wish_list': [
                {
                    'id': ''
                }
            ],
            'wish_list_tv': [
                {
                    'id': ''
                }
            ]

        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json,
                         {'wish_list': [{'id': ['Must be a valid UUID.']}],
                          'wish_list_tv': [{'id': ['Must be a valid UUID.']}]})

    def test_null_data_put(self):
        input_data = {}
        expected_result = {
            'id': str(self.user_account.id),
            'user':
                {
                    'username': self.user.username,
                    'email': self.user.email
            },
            'wish_list': [
                {
                    'id': str(film.id),
                    'source_id': film.source_id,
                    'popularity': film.popularity,
                    'vote_average': film.vote_average,
                    'vote_count': film.vote_count,
                    'poster_path': film.poster_path,
                    'backdrop_path': film.backdrop_path,
                    'original_language': film.original_language,
                    'type': film.type,
                    'overview': film.overview,
                    'title': film.title,
                    'original_title': film.original_title,
                    'release_date': film.release_date
                }
                for film in self.user_account.wish_list.all()
            ],
            'wish_list_tv': [
                {
                    'id': str(tv.id),
                    'source_id': tv.source_id,
                    'popularity': tv.popularity,
                    'vote_average': tv.vote_average,
                    'vote_count': tv.vote_count,
                    'poster_path': tv.poster_path,
                    'backdrop_path': tv.backdrop_path,
                    'original_language': tv.original_language,
                    'type': tv.type,
                    'overview': tv.overview,
                    'name': tv.name,
                    'original_name': tv.original_name,
                    'first_air_date': tv.first_air_date
                }
                for tv in self.user_account.wish_list_tv.all()
            ]
        }
        response = self.client.put(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_result)

    def test_positive_delete(self):
        input_data = {
            "films_ids": [
                {
                    "id": str(self.user_account.wish_list.all()[0].id)
                }
            ],
            "tvs_ids": [
                {
                    "id": str(self.user_account.wish_list_tv.all()[0].id)
                }
            ]
        }
        len_wish_list_before = len(self.user_account.wish_list.all())
        len_wish_list_tv_before = len(self.user_account.wish_list_tv.all())
        response = self.client.delete(self.url, format='json', data=input_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(len_wish_list_before, len(self.user_account.wish_list.all()))
        self.assertNotEqual(len_wish_list_tv_before, len(self.user_account.wish_list_tv.all()))

    def test_no_film_in_wish_list_delete(self):
        input_data = {
            "films_ids": [
                {
                    "id": ''
                }
            ]
        }
        len_wish_list_before = len(self.user_account.wish_list.all())
        response = self.client.delete(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'films_ids': [{'id': ['Must be a valid UUID.']}]})
        self.assertEqual(len_wish_list_before, len(self.user_account.wish_list.all()))

    def test_no_tv_in_wish_list_tv_delete(self):
        input_data = {
            "tvs_ids": [
                {
                    "id": ''
                }
            ]
        }
        len_wish_list_tv_before = len(self.user_account.wish_list_tv.all())
        response = self.client.delete(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'tvs_ids': [{'id': ['Must be a valid UUID.']}]})
        self.assertEqual(len_wish_list_tv_before, len(self.user_account.wish_list_tv.all()))
