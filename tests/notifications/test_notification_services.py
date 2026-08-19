"""Unit tests for ledger.notifications.services."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from model_bakery import baker

from ledger.notifications.constants import MESSAGE_TYPE_TRANSFER_RECEIVED
from ledger.notifications.services import notify_transfer_received
from ledger.transactions.models import TransactionLedger
from ledger.wallets.models import Wallet


@pytest.mark.django_db
class TestNotifyTransferReceived:
    """Tests for notify_transfer_received service."""

    def test_sends_notification_to_receiver_channel(self, user, other_user):
        """happy path: sends a transfer notification to the receiver's channel group."""
        sender_wallet = baker.make(Wallet, user=user, currency="USD", balance=500)
        receiver_wallet = baker.make(Wallet, user=other_user, currency="USD", balance=100)
        ledger_entry = baker.make(
            TransactionLedger,
            idempotency_key=uuid4(),
            transaction_type=TransactionLedger.TransactionType.TRANSFER,
            status=TransactionLedger.Status.COMPLETED,
            amount=75,
            currency="USD",
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
        )

        with patch(
            "ledger.notifications.services.notification_services.get_channel_layer"
        ) as mock_get_layer:
            mock_layer = MagicMock()
            mock_get_layer.return_value = mock_layer
            mock_layer.group_send = MagicMock()

            with patch(
                "ledger.notifications.services.notification_services.async_to_sync",
                side_effect=lambda func: func,
            ):
                notify_transfer_received(ledger_entry=ledger_entry)

            mock_layer.group_send.assert_called_once()
            call_args = mock_layer.group_send.call_args
            event = call_args[0][1]
            assert event["type"] == "transfer.received"
            payload = event["payload"]
            assert payload["sender_username"] == user.username
            assert payload["amount"] == 75
            assert payload["currency"] == "USD"
            assert payload["wallet_id"] == receiver_wallet.id

    def test_skips_when_no_receiver_wallet(self, user):
        """happy path: does nothing when receiver_wallet is None (deposit)."""
        sender_wallet = baker.make(Wallet, user=user, currency="USD")
        ledger_entry = baker.make(
            TransactionLedger,
            idempotency_key=uuid4(),
            transaction_type=TransactionLedger.TransactionType.WITHDRAWAL,
            status=TransactionLedger.Status.COMPLETED,
            amount=10,
            currency="USD",
            sender_wallet=sender_wallet,
            receiver_wallet=None,
        )

        with patch(
            "ledger.notifications.services.notification_services.get_channel_layer"
        ) as mock_get_layer:
            notify_transfer_received(ledger_entry=ledger_entry)
            mock_get_layer.assert_not_called()

    def test_skips_when_no_sender_wallet(self, user):
        """happy path: does nothing when sender_wallet is None (deposit)."""
        receiver_wallet = baker.make(Wallet, user=user, currency="USD")
        ledger_entry = baker.make(
            TransactionLedger,
            idempotency_key=uuid4(),
            transaction_type=TransactionLedger.TransactionType.DEPOSIT,
            status=TransactionLedger.Status.COMPLETED,
            amount=10,
            currency="USD",
            sender_wallet=None,
            receiver_wallet=receiver_wallet,
        )

        with patch(
            "ledger.notifications.services.notification_services.get_channel_layer"
        ) as mock_get_layer:
            notify_transfer_received(ledger_entry=ledger_entry)
            mock_get_layer.assert_not_called()
