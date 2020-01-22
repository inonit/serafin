from __future__ import unicode_literals
from django.contrib.auth.backends import ModelBackend

from django.contrib.auth import get_user_model
from django.db.models import Q

from tokens.tokens import token_generator
from users.models import User


class TokenBackend(ModelBackend):
    """
    Authenticate user against id and token
    """

    def authenticate(self, user_id, token):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        if token_generator.check_token(user_id, token):
            return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None

        return user

class EmailOrPhoneBackend(ModelBackend):
    """
    Authenticate user against email or phone number and password
    """

    def authenticate(self, username=None, password=None):
        my_user_model = get_user_model()
        try:
            user = my_user_model.objects.get(Q(email=username) | Q(phone=username))
            if user.check_password(password):
                return user
        except my_user_model.DoesNotExist:
            return None
        except:
            return None

    def get_user(self, user_id):
        my_user_model = get_user_model()
        try:
            return my_user_model.objects.get(pk=user_id)
        except my_user_model.DoesNotExist:
            return None
