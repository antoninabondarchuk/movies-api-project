from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Person
from movies.serializers import FilmSerializer, TvSerializer


class PersonSerializer(serializers.ModelSerializer):
    known_for = SerializerMethodField(read_only=True)
    known_for_tv = SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ("id", "popularity", "gender", "profile_path", "adult", "name",
                  "source_id", "known_for", "known_for_tv")

    def get_known_for(self, instance):
        films = instance.known_for.all().order_by('id')
        return FilmSerializer(films, many=True).data

    def get_known_for_tv(self, instance):
        tvs = instance.known_for_tv.all().order_by('id')
        return TvSerializer(tvs, many=True).data


class FilmTitleSerializer(serializers.Serializer):
    film_title = serializers.CharField()

    def validate_film_title(self, value):
        return value.replace('_', ' ')
