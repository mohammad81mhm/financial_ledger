from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from ledger.accounts.models import User


class JWTAuthMiddleware(BaseMiddleware):
    """Authenticate WebSocket connections using a JWT access token.

    The token is read from the ``token`` query-string parameter, validated
    with ``rest_framework_simplejwt``, and attached to ``scope["user"]``.
    """

    async def __call__(self, scope, receive, send):
        """Resolve the authenticated user and delegate to the inner application.

        Args:
            scope (dict): ASGI connection scope.
            receive (Callable): ASGI receive callable.
            send (Callable): ASGI send callable.

        Returns:
            Any: Result from the inner ASGI application.
        """
        scope["user"] = await self._resolve_user(scope=scope)
        return await super().__call__(scope, receive, send)

    async def _resolve_user(self, *, scope: dict) -> User | AnonymousUser:
        """Return the user for a WebSocket scope or an anonymous placeholder.

        Args:
            scope (dict): ASGI connection scope.

        Returns:
            User | AnonymousUser: Authenticated user when the token is valid,
                otherwise ``AnonymousUser``.
        """
        query_string = scope.get("query_string", b"").decode()
        token_values = parse_qs(query_string).get("token", [])
        if not token_values:
            return AnonymousUser()

        token = token_values[0]
        try:
            validated_token = AccessToken(token)
            user_id = validated_token["user_id"]
        except (InvalidToken, TokenError, KeyError):
            return AnonymousUser()

        return await self._get_user(user_id=user_id)

    @database_sync_to_async
    def _get_user(self, *, user_id: int) -> User | AnonymousUser:
        """Load an active user by primary key.

        Args:
            user_id (int): Primary key of the user to load.

        Returns:
            User | AnonymousUser: Active user when found, otherwise
                ``AnonymousUser``.
        """
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return AnonymousUser()
