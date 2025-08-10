from dj_rest_auth import views as auth_views
from django.contrib.auth import logout as django_logout
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING, NamedTuple
import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers
from .services import AuthAppService, full_logout

if TYPE_CHECKING:
    from main.models import UserType

User: 'UserType' = get_user_model()
logger = logging.getLogger(__name__)

class SignUpView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserSignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        try :
            service = AuthAppService()
            service.create_user(serializer.validated_data)
            return Response(
                {'detail': _('Confirmation email has been sent')},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e: 
            logger.error(f"registration failed {str(e)}")
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)


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
        return Response(
            {'detail': _('Password reset e-mail has been sent.')},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'detail': _('Password has been reset with the new password.')},
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(GenericAPIView):
    serializer_class = serializers.VerifyEmailSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data
        user = User.objects.get(email=email)

        if user.is_active:
            return Response(
                {'detail':_('Email already verified')},
                 status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = True
        user.save()
        return Response(
            {'detail': _('Email verified')},
            status=status.HTTP_200_OK,
        )
