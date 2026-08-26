from django.core.management.base import BaseCommand

from ledger.transactions.constants import DEFAULT_WALLET_TRANSFER_LIMIT
from ledger.wallets.models import Wallet


class Command(BaseCommand):
    """Reset every wallet's remaining transfer limit for a new period."""

    help = (
        "Set remaining_limit on all wallets to DEFAULT_WALLET_TRANSFER_LIMIT "
        f"({DEFAULT_WALLET_TRANSFER_LIMIT})."
    )

    def handle(self, *args, **options):
        """Restore remaining transfer limits on all wallets.

        Args:
            *args: Unused positional args.
            **options: Unused command options.
        """
        updated = Wallet.objects.update(remaining_limit=DEFAULT_WALLET_TRANSFER_LIMIT)
        self.stdout.write(
            self.style.SUCCESS(
                f"Reset remaining_limit to {DEFAULT_WALLET_TRANSFER_LIMIT} "
                f"on {updated} wallet(s)."
            )
        )
