import uuid
from datetime import datetime
from unittest import mock
import factory
import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.test import APIJWTClient
from comments.models import Comment
from tests.tests_movies import UserFactory, FilmFactory, GenreFactory


class CommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Comment

    path = factory.Sequence(lambda i: f'000{i % 9}')


class MovieCommentsViewTests(APITestCase):
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
        self.set_logined_user()
        self.genres = GenreFactory.create_batch(3)
        self.film = FilmFactory(genre_ids=self.genres)
        self.comments = CommentFactory.create_batch(9, film=self.film, author_id=self.user.id)
        self.comments.sort(key=lambda i: i.created_date, reverse=True)
        self.url = reverse('comments:movie_comments')

    def test_positive_get(self):
        self.url += f'?movie_id={str(self.film.id)}&movie_type={self.film.type}'
        expected_result = {
            "count": 9,
            "next": None,
            "previous": None,
            "results": [
                [{
                    "data": {
                        "author": str(self.user.id),
                        "film": str(self.film.id),
                        "tv": None,
                        "text": comment.text,
                        "created_date": comment.created_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    },
                    "id": str(comment.id)
                }]
                for comment in self.comments
            ]}
        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), 9)
        self.assertEqual(response_json, expected_result)

    def test_null_data_get(self):
        response = self.client.get(self.url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json,
                         {'movie_id': ['This field may not be null.'], 'movie_type': ['This field may not be null.']})

    def test_positive_add_comment(self):
        self.url += f'?movie_id={str(self.film.id)}&movie_type={self.film.type}'
        input_data = {
            'film': {
                'id': str(self.film.id)
            },
            'text': 'Comment.',
            'path': '0001'
        }
        mocked = datetime(2019, 12, 10, 0, 0, 0, 0, tzinfo=pytz.utc)
        expected_response = {
            'film':
                {
                    'id': str(self.film.id),
                    'source_id': self.film.source_id,
                    'popularity': self.film.popularity,
                    'vote_average': self.film.vote_average,
                    'vote_count': self.film.vote_count,
                    'poster_path': self.film.poster_path,
                    'backdrop_path': self.film.backdrop_path,
                    'original_language': self.film.original_language,
                    'type': self.film.type,
                    'overview': self.film.overview,
                    'title': self.film.title,
                    'original_title': self.film.original_title,
                    'release_date': self.film.release_date
                },
            'tv': None,
            'created_date': mocked.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'text': 'Comment.',
            'path': '00010001'
        }

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            response = self.client.post(self.url, format='json', data=input_data)
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response_json, expected_response)

    def test_unauthorized_comment(self):
        self.client.credentials()
        response_post = self.client.post(self.url, format='json',
                                         data={'film': {'id': str(self.film.id)}, 'text': 'Comment.', 'path': ''})
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

        response_delete = self.client.delete(self.url, format='json',
                                             data={'id': str(self.comments[0].id)})
        self.assertEqual(response_delete.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_null_data_add_comment(self):
        input_data = {}
        response = self.client.post(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'text': ['This field is required.'], 'path': ['This field is required.']})

    def test_delete_comment(self):
        input_data = {
            'id': str(self.comments[0].id)
        }
        response = self.client.delete(self.url, format='json', data=input_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_wrong_id_comment(self):
        input_data = {
            'id': str(uuid.uuid4())
        }
        response = self.client.delete(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, 'Sorry, no comment with such id.')

    def test_delete_null_data_comment(self):
        input_data = {}
        response = self.client.delete(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'id': ['This field is required.']})

    def test_delete_null_id_comment(self):
        input_data = {
            'id': ''
        }
        response = self.client.delete(self.url, format='json', data=input_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'id': ['Must be a valid UUID.']})
