from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from news.permissions import IsSuperUser
from news.serializers import NewsPostSerializer


class AddNewsPost(APIView):
    """
    To implement the ability to superusers add news to films and tvs.
    """
    permission_classes = (IsSuperUser, )

    @swagger_auto_schema(request_body=NewsPostSerializer)
    def post(self, request):
        """
        To allow superusers add news to films and tvs.
        :param request: HTTP request which contains info about post in the data attr.
        :return: HTTP response with status code 201, HTTP response with status code 400 with errors.
        """
        post_serializer = NewsPostSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(data=request.data, status=status.HTTP_201_CREATED)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
