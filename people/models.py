from django.db import models
from movies.models import Film, Tv
from movies.models import UUIDMixin


class Person(UUIDMixin):
    """
    For describing actors and directors of films and tvs.
    """
    popularity = models.FloatField(null=True)
    gender = models.IntegerField(null=True)
    profile_path = models.CharField(max_length=100, null=True)
    adult = models.BooleanField(null=True)
    name = models.CharField(max_length=1000, null=True)
    known_for = models.ManyToManyField(Film)
    known_for_tv = models.ManyToManyField(Tv)
    source_id = models.IntegerField(null=True)

    def __str__(self):
        return self.name

    def display_films(self):
        all_films = self.known_for.all().values("id", "title")\
            .union(self.known_for_tv.all().values("id", "name"))
        return ', '.join([film['title'] for film in all_films])

    display_films.short_description = 'Known for films and tvs'
