from decimal import Decimal
from uuid import uuid4

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from config.asgi import application
from ledger.authentication.services import create_token_pair
from ledger.notifications.constants import (
    MESSAGE_TYPE_PONG,
    MESSAGE_TYPE_TRANSFER_RECEIVED,
    WEBSOCKET_CLOSE_UNAUTHORIZED,
)
from ledger.transactions.services import transfer_between_wallets


@pytest.fixture
def access_token(user) -> str:
    """Return a JWT access token for the default user."""
    return create_token_pair(user=user)["access"]


@pytest.fixture
def other_access_token(other_user) -> str:
    """Return a JWT access token for the secondary user."""
    return create_token_pair(user=other_user)["access"]


def _build_communicator(*, token: str | None) -> WebsocketCommunicator:
    """Build a WebSocket communicator for the notifications endpoint.

    Args:
        token (str | None): JWT access token passed as a query parameter.

    Returns:
        WebsocketCommunicator: Configured async WebSocket test client.
    """
    path = "/ws/notifications/"
    if token is not None:
        path = f"{path}?token={token}"
    return WebsocketCommunicator(application, path)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connects_with_valid_jwt(access_token):
    """happy path: authenticated user connects to their notification channel."""
    communicator = _build_communicator(token=access_token)
    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_rejects_missing_token():
    """sad path: connection without a JWT token is rejected."""
    communicator = _build_communicator(token=None)
    connected, close_code = await communicator.connect()
    assert connected is False
    assert close_code == WEBSOCKET_CLOSE_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_rejects_invalid_token():
    """sad path: connection with an invalid JWT token is rejected."""
    communicator = _build_communicator(token="not-a-valid-token")
    connected, close_code = await communicator.connect()
    assert connected is False
    assert close_code == WEBSOCKET_CLOSE_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_echoes_sample_message(access_token):
    """happy path: client message receives a pong echo response."""
    communicator = _build_communicator(token=access_token)
    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"type": "ping"})
    response = await communicator.receive_json_from()
    assert response["type"] == MESSAGE_TYPE_PONG
    assert response["message"] == "WebSocket connection is active."
    assert response["echo"] == {"type": "ping"}

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_transfer_notifies_receiver_over_websocket(
    user,
    wallet,
    receiver_wallet,
    other_access_token,
):
    """happy path: completed transfer pushes a notification to the receiver socket."""
    communicator = _build_communicator(token=other_access_token)
    connected, _ = await communicator.connect()
    assert connected is True

    try:
        await database_sync_to_async(transfer_between_wallets)(
            user=user,
            data={
                "sender_wallet_id": wallet.id,
                "receiver_wallet_id": receiver_wallet.id,
                "amount": Decimal("25.50"),
                "idempotency_key": uuid4(),
            },
        )

        response = await communicator.receive_json_from()
        assert response["type"] == MESSAGE_TYPE_TRANSFER_RECEIVED
        assert response["sender_username"] == user.username
        assert response["amount"] == "25.50"
        assert response["currency"] == receiver_wallet.currency
        assert response["wallet_id"] == receiver_wallet.id
        assert response["transaction_id"]
    finally:
        await communicator.disconnect()
