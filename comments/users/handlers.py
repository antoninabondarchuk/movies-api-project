from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler
from logging import getLogger
from myproject import settings

logger = getLogger('users.views')


def custom_exception_handler(exception, context):
    response = exception_handler(exception, context)

    if response is not None:
        response['status_code'] = response.status_code

        if response.status_code >= 500:
            # if this is internal error, log it as exception
            logger.exception(str(exception))
            if not settings.DEBUG:
                return JsonResponse({
                    'error': 'Server Error (500)'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
