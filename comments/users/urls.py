from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create_user'),
    path('wish_list/', views.WishListView.as_view(), name='wish_list')
]
