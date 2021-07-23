from __future__ import unicode_literals
import re
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django.contrib.auth import get_user_model
from django.db.models import Q

from tokens.tokens import token_generator
from users.models import User


class TokenBackend(ModelBackend):
    """
    Authenticate user against id and token
    """

    def authenticate(self, request, user_id, token, **kwargs):
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
    def authenticate(self, request, username=None, password=None, **kwargs):
        my_user_model = get_user_model()
        try:
            user = my_user_model.objects.get(
                Q(email=username) | Q(phone=username))
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


class DigitPasswordValidator:
    """
    Validate whether the password has at least one digit.
    """

    def validate(self, password, user=None):
        if not re.search(r"[\d]+", password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_entirely_non_digits',
            )

    def get_help_text(self):
        return _("Your password must contain at least one digit.")
