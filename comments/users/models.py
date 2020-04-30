import uuid
from django.db import models
from movies.models import Film, Tv
from django.contrib.auth.models import AbstractUser
from movies.models import UUIDMixin


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class UserAccount(UUIDMixin):
    """
    Expands built-in Django User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wish_list = models.ManyToManyField(Film)
    wish_list_tv = models.ManyToManyField(Tv)

    def __str__(self):
        return self.user.username
