#!/usr/bin/env python
"""Root wrapper for Django manage.py.
This script forwards any command‑line arguments to the real manage.py
located at holbos_attendance/manage.py so you can run commands from the
project root (e.g., `python manage.py runserver`).
"""
import os
import subprocess
import sys

# Path to the inner manage.py
inner_manage = os.path.join(os.path.dirname(__file__), "holbos_attendance", "manage.py")

if not os.path.isfile(inner_manage):
    sys.exit("❌ Could not find inner manage.py at {}".format(inner_manage))

# Execute the inner script with the same Python interpreter
cmd = [sys.executable, inner_manage] + sys.argv[1:]
subprocess.run(cmd)
