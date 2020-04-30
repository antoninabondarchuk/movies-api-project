from rest_framework import serializers
from movies import serializers as mvserializers
from movies.models import Film, Tv
from news.models import NewsPost


class NewsPostSerializer(serializers.ModelSerializer):
    film = mvserializers.FilmSerializer(required=False, many=True)
    tv = mvserializers.TvSerializer(required=False, many=True)

    class Meta:
        model = NewsPost
        fields = '__all__'

    def create(self, validated_data):
        new_post = NewsPost()
        new_post.title = validated_data.get('title')
        new_post.overview = validated_data.get('overview')
        new_post.save()

        for film_data in validated_data.get('film', []):
            # film_data can take partial data from users up to FilmSerializer in movies.serializers.
            # Look there to get more info
            film_new = Film.objects.filter(**film_data).first()
            new_post.film.add(film_new)
            new_post.save()

        for tv_data in validated_data.get('tv', []):
            # tv_data can take partial data from users up to TvSerializer in movies.serializers
            # look there to get more info
            tv = Tv.objects.filter(**tv_data).first()
            new_post.tv.add(tv)
            new_post.save()
        return new_post
