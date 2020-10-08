from __future__ import unicode_literals
import re
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

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
