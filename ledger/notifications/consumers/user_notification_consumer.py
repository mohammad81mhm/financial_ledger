from channels.generic.websocket import AsyncJsonWebsocketConsumer

from ledger.notifications.constants import (
    MESSAGE_TYPE_PONG,
    MESSAGE_TYPE_TRANSFER_RECEIVED,
    USER_CHANNEL_GROUP_PREFIX,
    WEBSOCKET_CLOSE_UNAUTHORIZED,
)


def get_user_channel_name(*, user_id: int) -> str:
    """Build the channel-layer group name for a user.

    Args:
        user_id (int): Primary key of the user.

    Returns:
        str: Redis group name scoped to the given user.
    """
    return f"{USER_CHANNEL_GROUP_PREFIX}{user_id}"


class UserNotificationConsumer(AsyncJsonWebsocketConsumer):
    """Per-user WebSocket endpoint for real-time notifications.

    Authenticated users join a private group keyed by their user ID. Incoming
    client messages receive a simple echo response, and server-side events
    such as transfer receipts are pushed to connected clients.
    """

    async def connect(self):
        """Accept authenticated connections and subscribe to the user group."""
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=WEBSOCKET_CLOSE_UNAUTHORIZED)
            return

        self.group_name = get_user_channel_name(user_id=user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Leave the user group when the WebSocket disconnects.

        Args:
            close_code (int): WebSocket close code from the client or server.
        """
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Echo a sample response for any JSON message sent by the client.

        Args:
            content (dict): Parsed JSON payload from the client.
            **kwargs: Additional keyword arguments from Channels.
        """
        await self.send_json(
            {
                "type": MESSAGE_TYPE_PONG,
                "message": "WebSocket connection is active.",
                "echo": content,
            }
        )

    async def transfer_received(self, event):
        """Forward a transfer notification event to the connected client.

        Args:
            event (dict): Channel-layer event emitted by the notification
                service.
        """
        await self.send_json(
            {
                "type": MESSAGE_TYPE_TRANSFER_RECEIVED,
                **event["payload"],
            }
        )
