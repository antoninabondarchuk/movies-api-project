from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.test import APIJWTClient

from tests.tests_movies import UserFactory, FilmFactory, GenreFactory, TvGenreFactory, TvFactory


class AddNewsPostTests(APITestCase):
    client_class = APIJWTClient

    def set_logined_user_and_admin(self):
        get_token_url = reverse('token_obtain_pair')
        response_user = self.client.post(get_token_url,
                                         data={'username': self.user.username, 'password': 'pass'},
                                         format='json')
        token_user = response_user.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'{token_user}')

        response_admin = self.admin_client.post(get_token_url,
                                                data={'username': self.admin.username, 'password': 'pass'},
                                                format='json')
        token = response_admin.data['access']
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'{token}')

    def setUp(self):
        self.url = reverse('news:add_new_post')

        self.genres = GenreFactory.create_batch(2)
        self.films = FilmFactory.create_batch(2, genre_ids=self.genres)

        self.tv_genres = TvGenreFactory.create_batch(2)
        self.tvs = TvFactory.create_batch(2, genre_ids=self.tv_genres)

        self.guest = UserFactory()

        self.user = UserFactory()
        self.user.set_password('pass')
        self.user.save()

        self.admin_client = APIJWTClient()
        self.admin = UserFactory(is_superuser=True)
        self.admin.set_password('pass')
        self.admin.save()

        self.set_logined_user_and_admin()

    def test_positive_post(self):
        input_data = {
            "film": [
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
                for film in self.films
            ],
            "tv": [
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
                    "original_name": tv.original_language,
                    "first_air_date": tv.first_air_date
                }
                for tv in self.tvs
            ],
            "title": "string",
            "overview": "string"
        }
        response = self.admin_client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json, input_data)

    def test_unauthorized_post(self):
        input_data = {
            "film": [
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
                for film in self.films
            ],
            "tv": [
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
                    "original_name": tv.original_language,
                    "first_air_date": tv.first_air_date
                }
                for tv in self.tvs
            ],
            "title": "string",
            "overview": "string"
        }
        self.client.credentials()
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_json, {'detail': 'Authentication credentials were not provided.'})

    def test_not_admin_post(self):
        input_data = {
            "film": [
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
                for film in self.films
            ],
            "tv": [
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
                    "original_name": tv.original_language,
                    "first_air_date": tv.first_air_date
                }
                for tv in self.tvs
            ],
            "title": "string",
            "overview": "string"
        }
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_json, {'detail': 'You have to be a superuser to create news.'})

    def test_admin_null_data_post(self):
        input_data = {}
        expected_result = {
            "title": [
                "This field is required."
            ],
            "overview": [
                "This field is required."
            ]
        }
        response = self.admin_client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_result)

    def test_admin_empty_data_post(self):
        input_data = {
            "film": [
                {
                    "id": ""
                }
            ],
            "tv": [
                {
                    "id": ""
                }
            ],
            "title": "",
            "overview": ""
        }
        expected_result = {
            "film": [
                {
                    "id": ["Must be a valid UUID."]
                }
            ],
            "tv": [
                {
                    "id": ["Must be a valid UUID."]
                }
            ],
            "title": ["This field may not be blank."],
            "overview": ["This field may not be blank."]
        }
        response = self.admin_client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_result)
