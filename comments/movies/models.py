from django.db import models
import uuid


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin):
    source_id = models.IntegerField(null=True)
    title = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.title


class TvGenre(UUIDMixin):
    source_id = models.IntegerField(null=True)
    title = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.title if self.title else ""


class Film(UUIDMixin):
    source_id = models.IntegerField(null=True)
    popularity = models.FloatField(null=True)
    vote_count = models.IntegerField(null=True)
    video = models.BooleanField(null=True)
    poster_path = models.CharField(max_length=100, null=True)
    adult = models.BooleanField(default=False)
    backdrop_path = models.CharField(max_length=100, null=True)
    original_language = models.CharField(max_length=5, null=True)
    original_title = models.CharField(max_length=1000, null=True)
    genre_ids = models.ManyToManyField(Genre)
    title = models.CharField(max_length=1000, null=True)
    vote_average = models.FloatField(null=True)
    overview = models.TextField(blank=True, null=True)
    release_date = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=5, default="movie")

    def __str__(self):
        return self.title

    def display_genres(self):
        return ', '.join([genre.title for genre in self.genre_ids.all()])

    display_genres.short_description = 'Genres'


class Tv(UUIDMixin):
    source_id = models.IntegerField(null=True)
    poster_path = models.CharField(max_length=100, null=True)
    popularity = models.FloatField(null=True)
    backdrop_path = models.CharField(max_length=100, null=True)
    vote_average = models.FloatField(null=True)
    overview = models.TextField(blank=True, null=True)
    first_air_date = models.CharField(max_length=10, null=True)
    original_language = models.CharField(max_length=10, null=True)
    genre_ids = models.ManyToManyField(TvGenre)
    vote_count = models.IntegerField(null=True)
    name = models.CharField(max_length=1000, null=True)
    original_name = models.CharField(max_length=1000, null=True)
    type = models.CharField(max_length=5, default="tv", null=True)

    def __str__(self):
        return self.name

    def display_genres(self):
        return ', '.join([genre.title for genre in self.genre_ids.all()])

    display_genres.short_description = 'Genres'
