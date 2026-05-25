#!/usr/bin/env python
import os
import sys
from pathlib import Path


def main():
    BASE_DIR = Path(__file__).resolve().parent
    INNER_DIR = BASE_DIR / "holbos_attendance"

    sys.path.insert(0, str(INNER_DIR))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "holbos_attendance.holbos_project.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()