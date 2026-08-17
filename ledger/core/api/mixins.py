from collections.abc import Sequence
from typing import TYPE_CHECKING

from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

if TYPE_CHECKING:
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[type[BasePermission]]


class AuthMixin:
    """Default JWT authentication and IsAuthenticated permission for API views."""

    authentication_classes: Sequence[type[BaseAuthentication]] = [
        JWTAuthentication,
        SessionAuthentication,
    ]
    permission_classes: PermissionClassesType = (IsAuthenticated,)
