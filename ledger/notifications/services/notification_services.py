"""Services for pushing real-time WebSocket notifications."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ledger.notifications.consumers.user_notification_consumer import (
    get_user_channel_name,
)
from ledger.notifications.schemas.transfer_notification import (
    TransferReceivedNotification,
)
from ledger.transactions.models import TransactionLedger


def notify_transfer_received(*, ledger_entry: TransactionLedger) -> None:
    """Push a transfer notification to the receiver's WebSocket group.

    Args:
        ledger_entry (TransactionLedger): Completed transfer transaction with
            sender and receiver wallets populated.
    """
    receiver_wallet = ledger_entry.receiver_wallet
    sender_wallet = ledger_entry.sender_wallet
    if receiver_wallet is None or sender_wallet is None:
        return

    ledger_entry = TransactionLedger.objects.select_related(
        "sender_wallet__user",
        "receiver_wallet__user",
    ).get(pk=ledger_entry.pk)
    receiver_wallet = ledger_entry.receiver_wallet
    sender_wallet = ledger_entry.sender_wallet

    notification = TransferReceivedNotification(
        sender_username=sender_wallet.user.username,
        amount=int(ledger_entry.amount),
        currency=ledger_entry.currency,
        wallet_id=receiver_wallet.id,
        transaction_id=str(ledger_entry.id),
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        get_user_channel_name(user_id=receiver_wallet.user_id),
        {
            "type": "transfer.received",
            "payload": notification.to_dict(),
        },
    )
