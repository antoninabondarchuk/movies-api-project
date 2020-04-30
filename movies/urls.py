from django.urls import path
from . import views

urlpatterns = [
    path('', views.FilmsView.as_view(), name='movies'),
    path('api/', views.FilmsJsonView.as_view(), name='movies_json'),
    path('api/with_actor/', views.FilmsWithPersonJsonView.as_view(), name='films_with_person_json'),
    path('<str:actor_name>/', views.FilmsWithView.as_view(), name='films_with_actor'),
]
