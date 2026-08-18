from uuid import UUID

from django.db.models import Q, QuerySet

from ledger.accounts.models import User
from ledger.transactions.models import TransactionLedger


def get_transaction_by_idempotency_key(
    *, idempotency_key: UUID
) -> QuerySet[TransactionLedger]:
    """Return transactions filtered by idempotency key.

    Args:
        idempotency_key (UUID): Client-supplied idempotency key.

    Returns:
        QuerySet[TransactionLedger]: Queryset with zero or one row.
    """
    return TransactionLedger.objects.filter(idempotency_key=idempotency_key)


def get_transaction_by_id(*, transaction_id: UUID) -> QuerySet[TransactionLedger]:
    """Return transactions filtered by primary key.

    Args:
        transaction_id (UUID): Transaction primary key.

    Returns:
        QuerySet[TransactionLedger]: Queryset with zero or one row.
    """
    return TransactionLedger.objects.filter(id=transaction_id)


def get_transactions_for_user(*, user: User) -> QuerySet[TransactionLedger]:
    """Return transactions where the user owns the sender or receiver wallet.

    Args:
        user (User): User whose transaction history should be returned.

    Returns:
        QuerySet[TransactionLedger]: Matching transaction rows.
    """
    return TransactionLedger.objects.filter(
        Q(sender_wallet__user=user) | Q(receiver_wallet__user=user)
    ).select_related("sender_wallet", "receiver_wallet")
