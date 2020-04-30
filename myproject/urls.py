"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(openapi.Info(title="Snippets API",
                                           default_version='v1',
                                           description="Test description",
                                           terms_of_service="https://www.google.com/policies/terms/",
                                           contact=openapi.Contact(email="contact@snippets.local"),
                                           license=openapi.License(name="BSD License"),),
                              public=True,
                              permission_classes=(permissions.AllowAny,),)

urlpatterns = [
    path('admin/', admin.site.urls),
    # url to the administration panel
    path('movies/', include(('movies.urls', 'movies'), namespace='movies')),
    # url to movies app
    path('actors/', include(('people.urls', 'people'), namespace='people')),
    # url to people app (both actors and directors)
    path('user/', include(('users.urls', 'users'), namespace='users')),
    # url to users app to work with accounts
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # url to get token with refresh and access for existed users
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # url to refresh token for existed users
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url to manage and test API manually with UI Swagger
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # url to manage and test API manually with UI redoc
    path('news/', include(('news.urls', 'news'), namespace='news')),
    # url to news app to create and inform with them
    path('comments/', include(('comments.urls', 'comments'), namespace='comments')),
    # url to comments app
]
