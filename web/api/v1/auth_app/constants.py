from django.utils.translation import gettext_lazy as _

class AuthErrorMessage():
    NOT_VERIFIED = _('Email not verified')
    NOT_ACTIVE = _('Your account is not active. Please contact Your administrator')
    WRONG_CREDENTIALS = _('Entered email or password is incorrect')
    ALREADY_REGISTERED = _('User is already registered with this e-mail address')
    PASSWORD_NOT_MATCH = _('The two password fields did not match')
    EMAIL_NOT_EXIST = _('User with this email does not exist')
    LINK_ALREADY_ACTIVATED = _('This email address is already verified')
    LINK_EXPIRED = _('Confirmation link has expired')
    LINK_INVALID = _('Invalid link')

class FrontendPaths:
    VERIFY_EMAIL = 'verify-email/'
    RESET_PASSWORD_CONFRIM = 'api/v1/auth/password/reset/confirm/'