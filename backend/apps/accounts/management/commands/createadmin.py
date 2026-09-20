"""Bootstrap the FoodFlow platform admin user (idempotent).

Creates the user the admin dashboard's server-side routes authenticate to
Django with. Credentials come from --email/--password or the environment
(DJANGO_ADMIN_EMAIL / DJANGO_ADMIN_PASSWORD), not a hardcoded pair. Runs at
container start via docker-entrypoint.sh (after migrations).
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Role

DEFAULT_EMAIL = "admin@foodflow.local"
DEFAULT_PASSWORD = "admin123"


class Command(BaseCommand):
    help = "Create (or promote) the platform admin user. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=None, help="Admin email.")
        parser.add_argument("--password", default=None, help="Admin password.")
        parser.add_argument(
            "--update-password",
            action="store_true",
            help="Reset the password even if the user already exists.",
        )

    def handle(self, *args, **options):
        email = (
            options["email"] or os.environ.get("DJANGO_ADMIN_EMAIL") or DEFAULT_EMAIL
        ).strip().lower()
        password = (
            options["password"]
            or os.environ.get("DJANGO_ADMIN_PASSWORD")
            or DEFAULT_PASSWORD
        )

        User = get_user_model()
        user, created = User.objects.get_or_create(email=email)

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.role = Role.ADMIN
        if created or options["update_password"]:
            user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created platform admin: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Platform admin already exists: {email}"))
            if not options["update_password"]:
                self.stdout.write(
                    self.style.WARNING(
                        "Password left unchanged (use --update-password to reset it)."
                    )
                )