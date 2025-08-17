from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .constants import AuthErrorMessage
from api.v1.auth_app.services import AuthAppService

User = get_user_model()


class UserSignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, max_length=100)
    last_name = serializers.CharField(min_length=2, max_length=100)
    email = serializers.EmailField()
    password_1 = serializers.CharField(write_only=True, min_length=8)
    password_2 = serializers.CharField(write_only=True, min_length=8)

    def validate_password1(self, password: str):
        validate_password(password)
        return password

    def validate_email(self, email: str) -> str:
        if AuthAppService.is_user_exist(email):
            raise serializers.ValidationError(AuthErrorMessage.ALREADY_REGISTERED)
        return email

    def validate(self, data: dict):
        if data['password_1'] != data['password_2']:
            raise serializers.ValidationError({'password_2': AuthErrorMessage.PASSWORD_NOT_MATCH})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def validate(self, data: dict):
        email = data.get('email')
        password = data.get('password')
        user = self.authenticate(email=email, password=password)
        if not user:
            user = AuthAppService.get_user(email)
            if not user:
                msg = {'email': AuthErrorMessage.WRONG_CREDENTIALS}#wrong credentials
                raise serializers.ValidationError(msg)
            if not user.is_active:
                msg = {'email': AuthErrorMessage.NOT_ACTIVE} # not active
                raise serializers.ValidationError(msg)
            msg = {'email': AuthErrorMessage.WRONG_CREDENTIALS} # wrong credentials
            raise serializers.ValidationError(msg)
        data['user'] = user
        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            msg = {'email':AuthErrorMessage.EMAIL_NOT_EXIST}#email not exi
            raise serializers.ValidationError(msg)

class PasswordResetConfirmSerializer(serializers.Serializer):
    password_1 = serializers.CharField(min_length=8, max_length=64)
    password_2 = serializers.CharField(min_length=8, max_length=64)
    uid = serializers.CharField()
    token = serializers.CharField()


class VerifyEmailSerializer(serializers.Serializer):
    key = serializers.CharField()

    

