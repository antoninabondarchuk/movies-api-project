from rest_framework import serializers
from movies.models import Film, Tv
from users.models import User
from .models import UserAccount
from movies.serializers import FilmSerializer, TvSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Used for creating new users. Using only username and password.
    """
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}


class UserAccountSerializer(serializers.ModelSerializer):
    """
    The main aim is to work with user's wish list.
    """
    user = UserSerializer()
    wish_list = FilmSerializer(required=False, many=True)
    wish_list_tv = TvSerializer(required=False, many=True)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        user = User()
        user.username = user_data['username']
        user.email = user_data['email']
        user.set_password(password)
        user.save()
        validated_data['user'] = user
        user_account = UserAccount.objects.create(**validated_data)
        return user_account

    def update(self, instance, validated_data):
        """
        Adds new films and tvs to wish lists.
        :param instance: UserAccount instance.
        :param validated_data: validated data from UserAccountSerializer.
        :return: UserAccount instance with updated wish lists.
        """

        for film_data in validated_data.get('wish_list', []):
            # film_data can take partial data from users up to FilmSerializer in movies.serializers.
            # Look there to get more info
            film = Film.objects.filter(**film_data).first()
            instance.wish_list.add(film)
            instance.wish_list.all().order_by('id')
            instance.save()

        for tv_data in validated_data.get('wish_list_tv', []):
            # tv_data can take partial data from users up to TvSerializer in movies.serializers
            # look there to get more info
            tv = Tv.objects.filter(**tv_data).first()
            instance.wish_list_tv.add(tv)
            instance.wish_list_tv.all().order_by('id')
            instance.save()

        return instance

    class Meta:
        model = UserAccount
        fields = '__all__'


class DeleteFilmTvSerializer(serializers.Serializer):
    """
    For unique identification of films and tvs.
    """
    id = serializers.UUIDField()


class DeleteManyFilmTvSerializer(serializers.Serializer):
    """
    To remove films and tvs from wish lists separately.
    """
    films_ids = DeleteFilmTvSerializer(many=True, required=False)
    tvs_ids = DeleteFilmTvSerializer(many=True, required=False)
