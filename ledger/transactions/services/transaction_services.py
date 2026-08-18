from decimal import Decimal
from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, ValidationError

from ledger.accounts.models import User
from ledger.core.exceptions import ApplicationError
from ledger.notifications.services import notify_transfer_received
from ledger.transactions.constants import MONITORING_THRESHOLD
from ledger.transactions.models import TransactionLedger
from ledger.transactions.selectors.transaction_selectors import (
    get_transaction_by_idempotency_key,
)
from ledger.transactions.tasks.monitoring_tasks import notify_monitoring_team
from ledger.wallets.models import Wallet
from ledger.wallets.selectors.wallet_selectors import get_wallet_for_user_by_id


def _validate_amount(*, amount: Decimal) -> None:
    """Validate that an amount is positive and limited to two decimal places.

    Args:
        amount (Decimal): Amount supplied by the client.

    Raises:
        ValidationError: When the amount is zero, negative, or too precise.
    """
    if amount <= Decimal("0.00"):
        raise ValidationError(_("Amount must be greater than zero."))

    quantized = amount.quantize(Decimal("0.01"))
    if amount != quantized:
        raise ValidationError(_("Amount cannot have more than 2 decimal places."))


def _get_existing_idempotent(*, idempotency_key: UUID) -> TransactionLedger | None:
    """Return an existing transaction for the given idempotency key.

    Args:
        idempotency_key (UUID): Client-supplied idempotency key.

    Returns:
        TransactionLedger | None: Existing transaction or ``None``.
    """
    return get_transaction_by_idempotency_key(
        idempotency_key=idempotency_key
    ).first()


def _resolve_idempotent_transaction(
    *, idempotency_key: UUID
) -> tuple[TransactionLedger, bool] | None:
    """Return an idempotent transaction result when the key already exists.

    Args:
        idempotency_key (UUID): Client-supplied idempotency key.

    Returns:
        tuple[TransactionLedger, bool] | None: Existing transaction marked as
            duplicate, or ``None`` when no row exists yet.
    """
    existing = _get_existing_idempotent(idempotency_key=idempotency_key)
    if existing is None:
        return None
    return existing, True


def _handle_idempotency_integrity_error(
    *, idempotency_key: UUID, exc: IntegrityError
) -> tuple[TransactionLedger, bool]:
    """Convert a duplicate-key race into an idempotent success response.

    Args:
        idempotency_key (UUID): Client-supplied idempotency key.
        exc (IntegrityError): Integrity error raised during insert.

    Returns:
        tuple[TransactionLedger, bool]: Existing transaction marked as duplicate.

    Raises:
        IntegrityError: When the error is unrelated to idempotency.
    """
    existing = _get_existing_idempotent(idempotency_key=idempotency_key)
    if existing is None:
        raise exc
    return existing, True


def _ensure_wallet_owned_by_user(*, user: User, wallet_id: int) -> None:
    """Ensure the wallet belongs to the given user.

    Args:
        user (User): Expected wallet owner.
        wallet_id (int): Wallet primary key.

    Raises:
        NotFound: When the wallet is missing or owned by another user.
    """
    if not get_wallet_for_user_by_id(user=user, wallet_id=wallet_id).exists():
        raise NotFound


def _lock_wallet_by_id(*, wallet_id: int) -> Wallet:
    """Lock a single wallet row for update.

    Args:
        wallet_id (int): Wallet primary key.

    Returns:
        Wallet: Locked wallet instance.

    Raises:
        NotFound: When the wallet does not exist.
    """
    try:
        return Wallet.objects.select_for_update().get(id=wallet_id)
    except Wallet.DoesNotExist as exc:
        raise NotFound from exc


def _lock_wallets(*, wallet_ids: list[int]) -> list[Wallet]:
    """Lock multiple wallet rows in ascending ID order.

    Args:
        wallet_ids (list[int]): Wallet primary keys to lock.

    Returns:
        list[Wallet]: Locked wallet instances ordered by primary key.
    """
    ordered_ids = sorted(set(wallet_ids))
    return list(
        Wallet.objects.select_for_update()
        .filter(id__in=ordered_ids)
        .order_by("id")
    )


def _ensure_sufficient_balance(*, wallet: Wallet, amount: Decimal) -> None:
    """Ensure a wallet has enough balance for a debit.

    Args:
        wallet (Wallet): Wallet being debited.
        amount (Decimal): Amount to deduct.

    Raises:
        ApplicationError: When the wallet balance is insufficient.
    """
    if wallet.balance < amount:
        raise ApplicationError(
            _("Insufficient balance."),
            code="insufficient_balance",
        )


def _increase_wallet_balance(*, wallet_id: int, amount: Decimal) -> None:
    """Atomically increase a wallet balance.

    Args:
        wallet_id (int): Wallet primary key.
        amount (Decimal): Amount to add.
    """
    Wallet.objects.filter(id=wallet_id).update(balance=F("balance") + amount)


def _decrease_wallet_balance(*, wallet_id: int, amount: Decimal) -> None:
    """Atomically decrease a wallet balance.

    Args:
        wallet_id (int): Wallet primary key.
        amount (Decimal): Amount to subtract.
    """
    Wallet.objects.filter(id=wallet_id).update(balance=F("balance") - amount)


def create_transaction_ledger(
    *,
    idempotency_key: UUID,
    transaction_type: str,
    amount: Decimal,
    currency: str,
    description: str,
    sender_wallet: Wallet | None = None,
    receiver_wallet: Wallet | None = None,
) -> TransactionLedger:
    """Create and persist an immutable transaction ledger entry.

    Args:
        idempotency_key (UUID): Client-supplied idempotency key.
        transaction_type (str): One of ``TransactionLedger.TransactionType``.
        amount (Decimal): Transaction amount.
        currency (str): Currency code for the transaction.
        description (str): Optional transaction note.
        sender_wallet (Wallet | None): Wallet debited for withdrawals and transfers.
        receiver_wallet (Wallet | None): Wallet credited for deposits and transfers.

    Returns:
        TransactionLedger: Newly created ledger entry with ``COMPLETED`` status.
    """
    ledger_entry = TransactionLedger(
        idempotency_key=idempotency_key,
        transaction_type=transaction_type,
        status=TransactionLedger.Status.COMPLETED,
        amount=amount,
        currency=currency,
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        description=description,
    )
    ledger_entry.full_clean()
    ledger_entry.save()
    return ledger_entry


def _schedule_monitoring_if_needed(
    *, ledger_entry: TransactionLedger, amount: Decimal
) -> None:
    """Schedule a monitoring alert after commit for high-value transfers.

    Args:
        ledger_entry (TransactionLedger): Completed transfer transaction.
        amount (Decimal): Transfer amount.
    """
    if amount <= MONITORING_THRESHOLD:
        return

    transaction.on_commit(
        lambda: notify_monitoring_team.delay(transaction_id=str(ledger_entry.id))
    )


@transaction.atomic
def credit_increase(
    *, user: User, wallet_id: int, data: dict
) -> tuple[TransactionLedger, bool]:
    """Credit a wallet and record a deposit transaction.

    Args:
        user (User): Owner of the wallet being credited.
        wallet_id (int): Primary key of the target wallet.
        data (dict): Validated payload with ``amount``, ``idempotency_key``, and
            optional ``description``.

    Returns:
        tuple[TransactionLedger, bool]: Created or existing transaction and
            whether the record already existed.

    Raises:
        NotFound: When the wallet does not belong to the user.
        ValidationError: When the amount is invalid.
    """
    _ensure_wallet_owned_by_user(user=user, wallet_id=wallet_id)

    idempotency_key = data["idempotency_key"]
    idempotent_result = _resolve_idempotent_transaction(
        idempotency_key=idempotency_key
    )
    if idempotent_result is not None:
        return idempotent_result

    amount = data["amount"]
    description = data.get("description", "")
    _validate_amount(amount=amount)

    try:
        wallet = _lock_wallet_by_id(wallet_id=wallet_id)
        ledger_entry = create_transaction_ledger(
            idempotency_key=idempotency_key,
            transaction_type=TransactionLedger.TransactionType.DEPOSIT,
            amount=amount,
            currency=wallet.currency,
            receiver_wallet=wallet,
            description=description,
        )
        _increase_wallet_balance(wallet_id=wallet_id, amount=amount)
        return ledger_entry, False
    except IntegrityError as exc:
        return _handle_idempotency_integrity_error(
            idempotency_key=idempotency_key,
            exc=exc,
        )


@transaction.atomic
def credit_decrease(
    *, user: User, wallet_id: int, data: dict
) -> tuple[TransactionLedger, bool]:
    """Debit a wallet and record a withdrawal transaction.

    Args:
        user (User): Owner of the wallet being debited.
        wallet_id (int): Primary key of the target wallet.
        data (dict): Validated payload with ``amount``, ``idempotency_key``, and
            optional ``description``.

    Returns:
        tuple[TransactionLedger, bool]: Created or existing transaction and
            whether the record already existed.

    Raises:
        NotFound: When the wallet does not belong to the user.
        ValidationError: When the amount is invalid.
        ApplicationError: When the wallet balance is insufficient.
    """
    _ensure_wallet_owned_by_user(user=user, wallet_id=wallet_id)

    idempotency_key = data["idempotency_key"]
    idempotent_result = _resolve_idempotent_transaction(
        idempotency_key=idempotency_key
    )
    if idempotent_result is not None:
        return idempotent_result

    amount = data["amount"]
    description = data.get("description", "")
    _validate_amount(amount=amount)

    try:
        wallet = _lock_wallet_by_id(wallet_id=wallet_id)
        _ensure_sufficient_balance(wallet=wallet, amount=amount)
        ledger_entry = create_transaction_ledger(
            idempotency_key=idempotency_key,
            transaction_type=TransactionLedger.TransactionType.WITHDRAWAL,
            amount=amount,
            currency=wallet.currency,
            sender_wallet=wallet,
            description=description,
        )
        _decrease_wallet_balance(wallet_id=wallet_id, amount=amount)
        return ledger_entry, False
    except IntegrityError as exc:
        return _handle_idempotency_integrity_error(
            idempotency_key=idempotency_key,
            exc=exc,
        )


@transaction.atomic
def transfer_between_wallets(
    *, user: User, data: dict
) -> tuple[TransactionLedger, bool]:
    """Transfer funds between two wallets atomically.

    Args:
        user (User): Owner of the sender wallet.
        data (dict): Validated payload with ``sender_wallet_id``,
            ``receiver_wallet_id``, ``amount``, ``idempotency_key``, and optional
            ``description``.

    Returns:
        tuple[TransactionLedger, bool]: Created or existing transaction and
            whether the record already existed.

    Raises:
        NotFound: When the sender wallet does not belong to the user or a wallet
            is missing.
        ValidationError: When inputs are invalid.
        ApplicationError: When currencies differ or balance is insufficient.
    """
    sender_wallet_id = data["sender_wallet_id"]
    receiver_wallet_id = data["receiver_wallet_id"]
    idempotency_key = data["idempotency_key"]

    _ensure_wallet_owned_by_user(user=user, wallet_id=sender_wallet_id)

    idempotent_result = _resolve_idempotent_transaction(
        idempotency_key=idempotency_key
    )
    if idempotent_result is not None:
        return idempotent_result

    amount = data["amount"]
    description = data.get("description", "")
    _validate_amount(amount=amount)

    if sender_wallet_id == receiver_wallet_id:
        raise ValidationError(_("Sender and receiver wallets must be different."))

    try:
        locked_wallets = _lock_wallets(
            wallet_ids=[sender_wallet_id, receiver_wallet_id]
        )
        wallets_by_id = {wallet.id: wallet for wallet in locked_wallets}

        if len(wallets_by_id) != 2:
            raise NotFound

        sender_wallet = wallets_by_id[sender_wallet_id]
        receiver_wallet = wallets_by_id[receiver_wallet_id]

        if sender_wallet.currency != receiver_wallet.currency:
            raise ApplicationError(
                _("Wallets must share the same currency."),
                code="currency_mismatch",
            )

        _ensure_sufficient_balance(wallet=sender_wallet, amount=amount)

        ledger_entry = create_transaction_ledger(
            idempotency_key=idempotency_key,
            transaction_type=TransactionLedger.TransactionType.TRANSFER,
            amount=amount,
            currency=sender_wallet.currency,
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
            description=description,
        )
        _decrease_wallet_balance(wallet_id=sender_wallet_id, amount=amount)
        _increase_wallet_balance(wallet_id=receiver_wallet_id, amount=amount)
        _schedule_monitoring_if_needed(ledger_entry=ledger_entry, amount=amount)
        transaction.on_commit(
            lambda: notify_transfer_received(ledger_entry=ledger_entry)
        )
        return ledger_entry, False
    except IntegrityError as exc:
        return _handle_idempotency_integrity_error(
            idempotency_key=idempotency_key,
            exc=exc,
        )
