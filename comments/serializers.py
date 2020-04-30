from django.http import Http404
from rest_framework import serializers
from comments.models import Comment
from movies.models import Film, Tv
from movies.serializers import FilmSerializer, TvSerializer
from users.models import User


class CommentSerializer(serializers.ModelSerializer):
    """
    Used for creating new comments.
    """
    film = FilmSerializer(required=False)
    tv = TvSerializer(required=False)
    path = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = Comment
        fields = ('film', 'tv', 'created_date', 'text', 'path', )

    def create(self, validated_data):
        """
        To create new Comment instance using path of parent comment. May raise HTTP_404.
        :param validated_data: valid data for new Comment instance.
        :return: new instance of Comment
                 or HTTP response with status code 404 if no parent with path in valid data.
        """
        parent_path = validated_data.get('path')
        comment_text = validated_data.get('text')
        user_obj = User.objects.get(username=self.context['request'].user)
        try:
            film_obj = Film.objects.get(id=validated_data.get('film', dict()).get('id'))
        except Film.DoesNotExist:
            film_obj = None

        try:
            tv_obj = Tv.objects.get(id=validated_data.get('tv', dict()).get('id'))
        except Tv.DoesNotExist:
            tv_obj = None

        if not parent_path:
            new_comment = Comment.add_root(author=user_obj, film=film_obj, tv=tv_obj, text=comment_text)
        else:
            try:
                parent_comment = Comment.objects.get(path=parent_path)
                new_comment = parent_comment.add_child(author=user_obj, film=film_obj, tv=tv_obj, text=comment_text)
            except Comment.DoesNotExist:
                raise Http404('No parent comment with such path to add child.')

        return new_comment


class MovieSerializer(serializers.Serializer):
    """
    For working with object? according to the input data about film or tv.
    """
    movie_id = serializers.UUIDField()
    movie_type = serializers.CharField(max_length=10)

    @staticmethod
    def get_movie(validated_data):
        """
        To return object of type user wanted to.
        :param validated_data: valid data with id and object type.
        :return: Film or Tv object or
                 HTTP response with status code 404 if no such object in DB.
        """
        movie_type = validated_data.get('movie_type')
        movie_id = validated_data.get('movie_id')
        try:
            if movie_type == 'movie':
                return Film.objects.get(id=movie_id)
            return Tv.objects.get(id=movie_id)
        except (Film.DoesNotExist, Tv.DoesNotExist):
            return None


class RootCommentSerializer(serializers.Serializer):
    """
    To correct serialization of comment tree using parent comments
    and built-in method for nested representation.
    """
    comments = CommentSerializer(many=True)

    def to_representation(self, instance):
        if isinstance(instance, Comment):
            return Comment.dump_bulk(instance)
        return instance


class DeleteCommentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
