import requests
from myproject.celery import app
from .models import Film, Genre, Tv, TvGenre
import logging


API_KEY = '7ade7d202b652e6ff759b3143ebf1428'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6'
HEADERS = {'user-agent': USER_AGENT}
PAYLOAD = {'api_key': API_KEY,
           'language': 'en-US',
           'page': 1}


logger = logging.getLogger()


def get_paginated_list(url):
    pages_results = []
    total_pages = requests.get(url, headers=HEADERS, params=PAYLOAD).json()['total_pages']

    while PAYLOAD['page'] <= total_pages:
        response = requests.get(url, headers=HEADERS, params=PAYLOAD)
        pages_results += (response.json()['results'])
        PAYLOAD['page'] += 1

    return pages_results


@app.task
def get_genres(genres_url):
    genres = requests.get(genres_url, headers=HEADERS, params=PAYLOAD).json()['genres']

    for genre_dict in genres:
        genre, _ = Genre.objects.get_or_create(source_id=genre_dict.get('id'))
        genre.title = genre_dict.get('name')
        genre.save()


@app.task
def get_paginated_films(url):

    films_list = get_paginated_list(url)

    for film_dict in films_list:
        film, _ = Film.objects.get_or_create(source_id=film_dict.get('id'))
        film.popularity = film_dict.get('popularity')
        film.vote_count = film_dict.get('vote_count')
        film.video = film_dict.get('video')
        film.poster_path = film_dict.get('poster_path')
        film.adult = film_dict.get('adult')
        film.backdrop_path = film_dict.get('backdrop_path')
        film.original_language = film_dict.get('original_language')
        film.original_title = film_dict.get('original_title')
        film.title = film_dict.get('title')
        film.vote_average = film_dict.get('vote_average')
        film.overview = film_dict.get('overview')
        film.release_date = film_dict.get('release_date')
        film.type = "movie"
        film.save()

        for film_genre in film_dict['genre_ids']:
            genre = Genre.objects.get(source_id=film_genre)
            film.genre_ids.add(genre)


@app.task
def get_tv_genres(genres_url):
    genres = requests.get(genres_url, headers=HEADERS, params=PAYLOAD).json()['genres']

    for genre_dict in genres:
        genre, _ = TvGenre.objects.get_or_create(source_id=genre_dict.get('id'))
        genre.title = genre_dict.get('name')
        genre.save()


@app.task
def get_paginated_tvs(url):
    tvs_list = get_paginated_list(url)

    for tv_dict in tvs_list:
        tv, _ = Tv.objects.get_or_create(source_id=tv_dict.get('id'))
        tv.poster_path = tv_dict.get('poster_path')
        tv.popularity = tv_dict.get('popularity')
        tv.backdrop_path = tv_dict.get('backdrop_path')
        tv.vote_average = tv_dict.get('vote_average')
        tv.overview = tv_dict.get('overview')
        tv.first_air_date = tv_dict.get('first_air_date')
        tv.original_language = tv_dict.get('original_language')
        tv.vote_count = tv_dict.get('vote_count')
        tv.name = tv_dict.get('name')
        tv.original_name = tv_dict.get('original_name')
        tv.type = "tv"
        tv.save()

        for tv_genre in tv_dict['genre_ids']:
            try:
                genre_tv = TvGenre.objects.get(source_id=tv_genre)
                tv.genre_ids.add(genre_tv)
            except TvGenre.DoesNotExist:
                try:
                    movie_genre = Genre.objects.get(source_id=tv_genre)
                    new_tv_genre = TvGenre()
                    new_tv_genre.title = movie_genre.title
                    new_tv_genre.source_id = movie_genre.source_id
                    new_tv_genre.save()
                    tv.genre_ids.add(new_tv_genre)
                except Genre.DoesNotExist:
                    logger.exception("Genre does not exist!")
