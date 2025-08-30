from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import urlencode, urljoin
import logging

from django.core import signing
from django.conf import settings
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.signing import BadSignature,SignatureExpired
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .constants import AuthErrorMessage, FrontendPaths
from api.email_services import BaseEmailHandler
from main.decorators import except_shell


if TYPE_CHECKING:
    from main.models import UserType


User: 'UserType' = get_user_model()
logger = logging.getLogger(__name__)

class PasswordResetDTO(NamedTuple):
    uid:str
    token:str
class CreateUserData(NamedTuple):
    first_name: str
    last_name: str
    email: str
    password_1: str
    password_2: str


class ConfirmationEmailHandler(BaseEmailHandler):

    def email_kwargs(self, **kwargs) -> dict:
        activate_url = kwargs.get('activate_url')
        exp_hours = kwargs.get('exp_hours')

        return {
            'subject': _('Register confirmation email'),
            'to_email': self.user.email,
            'context': {
                'user': self.user.full_name,
                'activate_url': activate_url,
                'expiration_hours':exp_hours 
            },
        }


class VerifyEmailManager:
    def __init__(self,user):
        self.user:UserType = user

    def _generate_confirmation_key(self)->str:
        return signing.dumps(self.user.id)
    
    def _generate_activate_url(self)->str:
        base_url = urljoin(settings.FRONTEND_URL,FrontendPaths.VERIFY_EMAIL)
        query_params:str = urlencode(
            {
                'key':self._generate_confirmation_key()
            },
            safe=':+',
        )
        return f"{base_url}?{query_params}"

    def send_confirmation_email(self):
        handler = ConfirmationEmailHandler(user=self.user,template_name='email/verify_email.html')
        activate_url = self._generate_activate_url()
        handler.send_email(
            activate_url=activate_url,
            expiration_hours=int(48*3600)
        )

    @staticmethod
    def verify_email_confirmation(key: str):
        try:
            user_id = signing.loads(key, max_age=48*3600)
            user = User.objects.get(id=user_id)
            if user.is_active:
                raise ValidationError(
                    AuthErrorMessage.USER_ALREADY_ACTIVATED,
                    code='link_already_activated')
            user.is_active = True
            user.save(update_fields=['is_active'])
            return user
        except SignatureExpired:
            raise ValidationError(
                AuthErrorMessage.LINK_EXPIRED,
                code="link_expired"
            )
        except BadSignature:
            raise ValidationError(
                AuthErrorMessage.LINK_INVALID,
                code="link_invalid"
            )

class PasswordReset:
    def __init__(self):
        self.token_gen = PasswordResetTokenGenerator()

    def _get_user(self,uid):
        user = User.objects.get()
    @transaction.atomic()
    def reset_password(self):
        pass
    
class PasswodResetMessageService:
    def __init__(self): 
        self.token_gen = PasswordResetTokenGenerator()

    @staticmethod
    def validate_email(value) ->bool:
        if user_ex:=User.objects.filter(email=value).exists():
            return user_ex
    
    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user(email: str) -> User:
        return User.objects.get(email=email)

    def _generate_uid(self,user_id:int)->str:
        return urlsafe_base64_encode(force_bytes(user_id))
    
    def _generate_token(self,user):
        return self.token_gen.make_token(user)
    
    def validate_token(self,user,token:str)->bool:
        return self.token_gen.check_token(user,token) 
    
    def generate(self,user)->PasswordResetDTO:
        uid = self._generate_uid(user.id)
        token = self._generate_token(user)
        return PasswordResetDTO(uid=uid,token=token)
    
    def gen_url(self,user)->str:
        FRONTEND_URL: str = settings.FRONTEND_URL
        FRONTEND_PATH = FrontendPaths.RESET_PASSWORD_CONFRIM

        dto = self.generate(user)

        params = {
            'uid':dto.uid,
            'token':dto.token
        }
        query_str = urlencode(params)
        base_url = urljoin(FRONTEND_URL,FRONTEND_PATH)
        return f'{base_url}?{query_str}'
    
    def send_reset_mail(self,email):
        self.user = self.get_user(email)
        handler = ConfirmationEmailHandler(user=self.user,template_name='email/reset_password.html')
        activate_url = self.gen_url(self.user)
        handler.send_email(
            activate_url=activate_url,
            expiration_hours=int(12*3600)
        )

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

        user = User.objects.create_user(
            email=data.email,
            first_name = data.first_name,
            last_name = data.last_name,
            is_active= False,
            password = data.password_1
        )
        self._send_confirmation_email(user)
        logger.info("User created") 
        return user
    
    def _send_confirmation_email(self,user):
        email_handler = VerifyEmailManager(user)
        email_handler.send_confirmation_email()

 
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
