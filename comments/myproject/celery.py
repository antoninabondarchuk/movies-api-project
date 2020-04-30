import os
from datetime import timedelta, datetime
from celery import Celery
from .settings import FILM_API_URL
# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-db-genres': {
        'task': 'movies.tasks.get_genres',
        'schedule': crontab(hour=1, minute=40),
        'args': (FILM_API_URL + 'genre/movie/list',)
    },
    'update-db-tv-genres': {
        'task': 'movies.tasks.get_tv_genres',
        'schedule': crontab(hour=1, minute=42),
        'args': (FILM_API_URL + 'genre/tv/list',)
    },
    'update-db-films': {
        'task': 'movies.tasks.get_paginated_films',
        'schedule': crontab(hour=1, minute=45),
        'args': (FILM_API_URL + 'discover/movie',)
    },
    'update-db-tvs': {
        'task': 'movies.tasks.get_paginated_tvs',
        'schedule': crontab(hour=2, minute=45),
        'args': (FILM_API_URL + 'discover/tv',)
    },
    'update-db-people': {
        'task': 'people.tasks.get_paginated_people',
        'schedule': crontab(hour=2, minute=15),
        'args': (FILM_API_URL + 'person/popular',)
    },
    'send-email-news': {
        'task': 'news.tasks.send_emails_news',
        'schedule': crontab(hour=1, minute=1),
        'args': (datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d'),)
    },

}
