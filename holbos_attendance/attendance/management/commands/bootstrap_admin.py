import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Safely create the configured production administrator if it is missing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Explicitly reset an existing administrator to the configured password.",
        )

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        self.stdout.write(f"Database connection verified ({connection.vendor}).")

        if settings.IS_RENDER and connection.vendor != "postgresql":
            raise CommandError(
                "Administrator bootstrap on Render requires PostgreSQL."
            )

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        reset_password = options["reset_password"]

        if not any((username, email, password)):
            if reset_password:
                raise CommandError(
                    "Set all DJANGO_SUPERUSER_* variables before requesting a password reset."
                )
            self.stdout.write(
                "Administrator bootstrap skipped; DJANGO_SUPERUSER_* variables are not configured."
            )
            return

        if not all((username, email, password)):
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, "
                "and DJANGO_SUPERUSER_PASSWORD together."
            )

        User = get_user_model()
        user = User._default_manager.filter(username=username).first()

        if user is not None:
            if not (user.is_active and user.is_staff and user.is_superuser):
                raise CommandError(
                    "The configured username already belongs to a non-administrator account. "
                    "No account data was changed."
                )
            if reset_password:
                self._validate_password(password, user)
                user.set_password(password)
                user.save(update_fields=["password"])
                self.stdout.write("Administrator password was explicitly reset.")
            else:
                self.stdout.write(
                    "Administrator already exists; its password was left unchanged."
                )
            return

        user = User(username=username, email=email, full_name=username)
        self._validate_password(password, user)

        try:
            with transaction.atomic():
                User._default_manager.db_manager(connection.alias).create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    full_name=username,
                )
        except IntegrityError as exc:
            existing_user = User._default_manager.filter(username=username).first()
            if existing_user is not None and (
                existing_user.is_active
                and existing_user.is_staff
                and existing_user.is_superuser
            ):
                self.stdout.write(
                    "Administrator already exists; its password was left unchanged."
                )
                return
            raise CommandError(
                "Administrator creation conflicted with existing account data. "
                "No existing account was changed."
            ) from exc

        self.stdout.write("Administrator account created.")

    @staticmethod
    def _validate_password(password, user):
        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError(
                "The configured administrator password does not meet Django's password policy."
            ) from exc
