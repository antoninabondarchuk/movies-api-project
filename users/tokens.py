from datetime import timedelta
from rest_framework_simplejwt.tokens import Token


class MyToken(Token):
    token_type = 'access'
    lifetime = timedelta(minutes=5)
