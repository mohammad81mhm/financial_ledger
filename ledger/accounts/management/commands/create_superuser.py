from django.core.management.base import BaseCommand
from rest_framework.exceptions import ValidationError

from ledger.accounts.constants import SUPERUSER_DATA
from ledger.accounts.services import create_superuser


class Command(BaseCommand):
    """Create the default superuser from accounts constants."""

    help = "Create the default superuser if it does not already exist."

    def handle(self, *args, **options):
        """Create or skip the bootstrap superuser.

        Args:
            *args: Unused positional args.
            **options: Unused command options.
        """
        try:
            user, created = create_superuser(data=SUPERUSER_DATA)
        except ValidationError as exc:
            self.stderr.write(self.style.ERROR(str(exc.detail)))
            return

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser {user.username}."))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser {user.username} already exists."))
