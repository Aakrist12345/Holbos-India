@echo off
cd holbos_project
call ..\venv\Scripts\activate.bat
python manage.py runserver
pause