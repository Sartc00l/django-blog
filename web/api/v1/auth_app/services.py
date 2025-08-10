from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import urlencode, urljoin
import logging

from django.core import signing
from django.core.signing import BadSignature,SignatureExpired
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from api.email_services import BaseEmailHandler

from main.decorators import except_shell

if TYPE_CHECKING:
    from main.models import UserType


User: 'UserType' = get_user_model()
logger = logging.getLogger(__name__)


class CreateUserData(NamedTuple):
    first_name: str
    last_name: str
    email: str
    password_1: str
    password_2: str


class ConfirmationEmailHandler(BaseEmailHandler):
    FRONTEND_URL = settings.FRONTEND_URL
    FRONTEND_PATH = 'verify-email/'
    TEMPLATE_NAME = 'email/verify_email.html'
    EXPIRATION_SECONDS = 48 * 3600


    def _generate_confrimation_key(self) -> str:
        signer = signing.TimestampSigner()
        return signer.sign(self.user.email)
    
    def _get_activate_url(self) -> str:
        url = urljoin(self.FRONTEND_URL, self.FRONTEND_PATH)
        query_params: str = urlencode(
            {
                'key': self._generate_confrimation_key(),
            },
            safe=':+',
        )
        return f'{url}?{query_params}'

    def email_kwargs(self, **kwargs) -> dict:
        return {
            'subject': _('Register confirmation email'),
            'to_email': self.user.email,
            'context': {
                'user': self.user.full_name,
                'activate_url': self._get_activate_url(),
                'expiration_hours': int(self.EXPIRATION_SECONDS / 3600)
            },
        }


class AuthAppService:
    @staticmethod
    def is_user_exist(email: str) -> bool:
        return User.objects.filter(email=email).exists()

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user(email: str) -> User:
        return User.objects.get(email=email)

    @transaction.atomic()
    def create_user(self, validated_data: dict):
        data = CreateUserData(**validated_data)

        user = User.objects.create(
            email=data.email,
            first_name = data.first_name,
            last_name = data.last_name,
            is_active= False,
            password = make_password(data.password_1)
        )
        self._send_confrimation_email(user)
        logger.info("Сделал юзера!!!!!!!")
        return user
    
    def _send_confrimation_email(self,user):
        email_handler = ConfirmationEmailHandler(user)
        email_handler.send_email()



def full_logout(request):
    response = Response({"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK)
    auth_cookie_name = settings.REST_AUTH['JWT_AUTH_COOKIE']
    refresh_cookie_name = settings.REST_AUTH['JWT_AUTH_REFRESH_COOKIE']

    response.delete_cookie(auth_cookie_name)
    refresh_token = request.COOKIES.get(refresh_cookie_name)
    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except KeyError:
        response.data = {"detail": _("Refresh token was not included in request data.")}
        response.status_code = status.HTTP_401_UNAUTHORIZED
    except (TokenError, AttributeError, TypeError) as error:
        if hasattr(error, 'args'):
            if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                response.data = {"detail": _(error.args[0])}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            else:
                response.data = {"detail": _("An error has occurred.")}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        else:
            response.data = {"detail": _("An error has occurred.")}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        message = _(
            "Neither cookies or blacklist are enabled, so the token "
            "has not been deleted server side. Please make sure the token is deleted client side."
        )
        response.data = {"detail": message}
        response.status_code = status.HTTP_200_OK
    return response
