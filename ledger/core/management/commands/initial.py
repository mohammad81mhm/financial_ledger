from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Run first-time initialization commands across the project."""

    help = "Bootstrap the system on first run."

    def handle(self, *args, **options):
        """Execute bootstrap sub-commands.

        Args:
            *args: Unused positional args.
            **options: Unused command options.
        """
        call_command("create_superuser", stdout=self.stdout, stderr=self.stderr)
        self.stdout.write(self.style.SUCCESS("Initialization complete."))
