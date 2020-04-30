from django.urls import path
from . import views

urlpatterns = [
    path('', views.MovieCommentsView.as_view(), name='movie_comments'),
]
