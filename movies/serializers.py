from rest_framework import serializers

from .models import Genre, TvGenre, Film, Tv


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("source_id", "title")


class TvGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TvGenre
        fields = ("source_id", "title")


class FilmSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    genres = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Film
        fields = ("id", "source_id", "popularity", "vote_average",
                  "vote_count", "poster_path", "backdrop_path",
                  "original_language", "type", "overview",
                  "title", "original_title", "release_date", "genres")


class TvSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    genres = TvGenreSerializer(read_only=True, many=True)

    class Meta:
        model = Tv
        fields = ("id", "source_id", "popularity", "vote_average",
                  "vote_count", "poster_path", "backdrop_path",
                  "original_language", "type", "overview",
                  "name", "original_name", "first_air_date", "genres")


class VoteSerializer(serializers.Serializer):
    tv = TvSerializer(required=False)
    film = FilmSerializer(required=False)
    vote = serializers.FloatField(min_value=0, max_value=10, write_only=True)

    def update(self, instance, validated_data):
        instance.vote_count += 1  # User voted
        user_vote = validated_data.get('vote')
        instance.vote_average += user_vote / instance.vote_count
        instance.vote_average = round(instance.vote_average, 1)
        instance.save()
        return instance

    @staticmethod
    def get_film_or_tv(film_data):
        """
        The function to decide whether user choose film or tv, according to the request data in film_data.
        :param film_data: HTTP request which contains info about movie type.
        :return: Film or Tv object according to the type or None if there is not such film or tv.
        """
        try:
            if 'film' in film_data and film_data['film'].get('id'):
                return Film.objects.get(id=film_data['film'].get('id'))
            return Tv.objects.get(id=film_data['tv']['id'])
        except (Film.DoesNotExist, Tv.DoesNotExist):
            return None


class ActorNameSerializer(serializers.Serializer):
    actor_name = serializers.CharField()

    def validate_actor_name(self, value):
        return value.replace('_', ' ')
