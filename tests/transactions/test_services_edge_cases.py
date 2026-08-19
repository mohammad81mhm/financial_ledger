"""Edge-case service tests for transaction operations."""

from uuid import uuid4

import pytest
from rest_framework.exceptions import NotFound, ValidationError

from ledger.core.exceptions import ApplicationError
from ledger.transactions.services import credit_decrease, credit_increase, transfer_between_wallets


@pytest.mark.django_db
class TestCreditDecreaseIdempotency:
    """Idempotency tests for credit_decrease."""

    def test_returns_existing_transaction_on_duplicate_key(self, user, wallet):
        """happy path: repeated credit decrease with same key returns original."""
        idempotency_key = uuid4()
        data = {"amount": 50, "idempotency_key": idempotency_key}

        first, first_dup = credit_decrease(user=user, wallet_id=wallet.id, data=data)
        second, second_dup = credit_decrease(user=user, wallet_id=wallet.id, data=data)

        wallet.refresh_from_db()

        assert first_dup is False
        assert second_dup is True
        assert first.id == second.id
        assert wallet.balance == 950


@pytest.mark.django_db
class TestZeroAmountValidation:
    """Zero amount rejection across all services."""

    def test_credit_increase_rejects_zero(self, user, wallet):
        """sad path: credit_increase rejects zero amount."""
        data = {"amount": 0, "idempotency_key": uuid4()}

        with pytest.raises(ValidationError, match="greater than zero"):
            credit_increase(user=user, wallet_id=wallet.id, data=data)

    def test_credit_decrease_rejects_zero(self, user, wallet):
        """sad path: credit_decrease rejects zero amount."""
        data = {"amount": 0, "idempotency_key": uuid4()}

        with pytest.raises(ValidationError, match="greater than zero"):
            credit_decrease(user=user, wallet_id=wallet.id, data=data)


@pytest.mark.django_db
class TestTransferEdgeCases:
    """Additional edge cases for transfer_between_wallets."""

    def test_rejects_insufficient_balance(self, user, wallet, receiver_wallet):
        """sad path: transfer fails when sender balance is too low."""
        data = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": receiver_wallet.id,
            "amount": 5000,
            "idempotency_key": uuid4(),
        }

        with pytest.raises(ApplicationError) as exc_info:
            transfer_between_wallets(user=user, data=data)

        assert exc_info.value.default_code == "insufficient_balance"

    def test_rejects_foreign_sender_wallet(self, user, other_user, receiver_wallet, wallet):
        """sad path: transfer fails when sender wallet does not belong to user."""
        data = {
            "sender_wallet_id": receiver_wallet.id,
            "receiver_wallet_id": wallet.id,
            "amount": 10,
            "idempotency_key": uuid4(),
        }

        with pytest.raises(NotFound):
            transfer_between_wallets(user=user, data=data)

    def test_credit_increase_rejects_foreign_wallet(self, user, receiver_wallet):
        """sad path: credit_increase fails when wallet belongs to another user."""
        data = {"amount": 10, "idempotency_key": uuid4()}

        with pytest.raises(NotFound):
            credit_increase(user=user, wallet_id=receiver_wallet.id, data=data)

    def test_credit_decrease_rejects_foreign_wallet(self, user, receiver_wallet):
        """sad path: credit_decrease fails when wallet belongs to another user."""
        data = {"amount": 10, "idempotency_key": uuid4()}

        with pytest.raises(NotFound):
            credit_decrease(user=user, wallet_id=receiver_wallet.id, data=data)
