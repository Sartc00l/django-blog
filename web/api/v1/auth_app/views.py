from dj_rest_auth import views as auth_views
from django.contrib.auth import logout as django_logout
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING, NamedTuple
import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError,ErrorDetail
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .constants import AuthErrorMessage
from . import serializers

from .services import (
    VerifyEmailManager,
    PasswodResetMessageService,
    AuthAppService, 
    full_logout)

if TYPE_CHECKING:
    from main.models import UserType

User: 'UserType' = get_user_model()
logger = logging.getLogger(__name__)

ERRORS_MAPPING = {
    'link_already_activated': {
        'detail': AuthErrorMessage.USER_ALREADY_ACTIVATED,
        'status': status.HTTP_400_BAD_REQUEST
    },
    'link_expired': {
        'detail': AuthErrorMessage.LINK_EXPIRED,
        'status': status.HTTP_410_GONE
    },
    'link_invalid': {
        'detail': AuthErrorMessage.LINK_INVALID,
        'status': status.HTTP_400_BAD_REQUEST
    }
}

class SignUpView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserSignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthAppService()
        service.create_user(serializer.validated_data)
        return Response(
            {'detail': _('Confirmation email has been sent')},
            status=status.HTTP_201_CREATED,
        )

class LoginView(auth_views.LoginView):
    serializer_class = serializers.LoginSerializer


class LogoutView(auth_views.LogoutView):
    allowed_methods = ('POST', 'OPTIONS')

    def session_logout(self):
        django_logout(self.request)

    def logout(self, request):
        response = full_logout(request)
        return response


class PasswordResetView(GenericAPIView):
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = PasswodResetMessageService()
        service.send_reset_mail(serializer.validated_data['email'])
        return Response(
            {'detail': _('Password reset e-mail has been sent.')},
            status=status.HTTP_200_OK,
        )


class PasswordResetValidateView(GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('Password has been reset with the new password.')},
            status=status.HTTP_200_OK,
        )


class PasswordResetValidateView(GenericAPIView):
    serializer_class = serializers.PasswordResetValidateSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {'detail': True},
            status=status.HTTP_200_OK,
        )

class VerifyEmailView(GenericAPIView): 
    serializer_class = serializers.VerifyEmailSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = VerifyEmailManager.verify_email_confirmation(serializer.validated_data['key'])
            return Response(
                {'detail': _('Email confirmed')},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            error_detail:ErrorDetail = e.detail[0]
            code = error_detail.code
            error = ERRORS_MAPPING.get(code)
            return Response(
                {'detail':error['detail']},
                status=error['status'],
            )