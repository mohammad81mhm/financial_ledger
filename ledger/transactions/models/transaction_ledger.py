import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ledger.core.models import BaseModel
from ledger.wallets.models import Wallet


class ImmutableTransactionError(Exception):
    """Raised when an attempt is made to update an immutable transaction record."""


class TransactionLedger(BaseModel):
    """Immutable ledger entry for wallet deposits, withdrawals, and transfers."""

    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", _("Deposit")
        WITHDRAWAL = "WITHDRAWAL", _("Withdrawal")
        TRANSFER = "TRANSFER", _("Transfer")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        COMPLETED = "COMPLETED", _("Completed")
        FAILED = "FAILED", _("Failed")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
        help_text="Unique identifier for this transaction.",
    )
    idempotency_key = models.UUIDField(
        unique=True,
        verbose_name=_("Idempotency key"),
        help_text="Client-supplied key that guarantees at-most-once processing.",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name=_("Transaction type"),
        help_text="Kind of wallet movement: deposit, withdrawal, or transfer.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
        help_text="Processing status of this transaction.",
    )
    amount = models.BigIntegerField(
        verbose_name=_("Amount"),
        help_text="Transaction amount in whole units of the wallet currency.",
    )
    currency = models.CharField(
        max_length=3,
        choices=Wallet.Currency.choices,
        verbose_name=_("Currency"),
        help_text="Currency code for this transaction.",
    )
    sender_wallet = models.ForeignKey(
        Wallet,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sent_transactions",
        verbose_name=_("Sender wallet"),
        help_text="Wallet debited for withdrawals and transfers.",
    )
    receiver_wallet = models.ForeignKey(
        Wallet,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="received_transactions",
        verbose_name=_("Receiver wallet"),
        help_text="Wallet credited for deposits and transfers.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text="Optional note describing this transaction.",
    )

    class Meta:
        verbose_name = _("transaction ledger entry")
        verbose_name_plural = _("transaction ledger entries")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["sender_wallet", "created_at"], name="tx_sender_created_idx"),
            models.Index(fields=["receiver_wallet", "created_at"], name="tx_receiver_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.transaction_type}:{self.id}"

    def save(self, *args, **kwargs) -> None:
        """Persist a new ledger entry and reject updates to existing rows."""
        if self.pk and TransactionLedger.objects.filter(pk=self.pk).exists():
            raise ImmutableTransactionError(
                "TransactionLedger records cannot be updated."
            )
        super().save(*args, **kwargs)
