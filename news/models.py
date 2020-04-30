from django.db import models
from movies.models import Film, Tv, UUIDMixin


class NewsPost(UUIDMixin):
    title = models.CharField(max_length=256)
    overview = models.TextField()
    film = models.ManyToManyField(Film, blank=True)
    tv = models.ManyToManyField(Tv, blank=True)
    publish_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def display_films(self):
        return ', '.join([film.title for film in self.film.all()])

    def display_tvs(self):
        return ', '.join([tv.name for tv in self.tv.all()])

    display_tvs.short_description = 'Tvs'
    display_films.short_description = 'Films'
