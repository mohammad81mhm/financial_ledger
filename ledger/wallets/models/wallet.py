from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ledger.core.models import BaseModel


class Wallet(BaseModel):
    """A user-owned wallet tied to a single currency and balance."""

    class Currency(models.TextChoices):
        USD = "USD", _("US dollar")
        EUR = "EUR", _("Euro")
        IRR = "IRR", _("Iranian rial")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="wallets",
        verbose_name=_("User"),
        help_text="Owner of this wallet.",
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        verbose_name=_("Currency"),
        help_text="Currency code for this wallet, such as USD, EUR, or IRR.",
    )
    balance = models.BigIntegerField(
        default=0,
        verbose_name=_("Balance"),
        help_text="Current wallet balance in whole units of the selected currency.",
    )

    remaining_limit = models.BigIntegerField(
        default=0,
        verbose_name=_("Remaining limit"),
        help_text="Remaining transferable amount for the current limitation period.",
    )

    class Meta:
        verbose_name = _("wallet")
        verbose_name_plural = _("wallets")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "currency"],
                name="unique_wallet_user_currency",
            ),
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(remaining_limit__gte=0),
                name="wallet_remaining_limit_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.currency}"
