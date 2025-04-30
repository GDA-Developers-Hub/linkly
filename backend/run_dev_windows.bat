@echo off
echo Creating virtual environment if it doesn't exist...
if not exist venv (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
)

echo Setting Django settings module...
set DJANGO_SETTINGS_MODULE=socialbu.settings_dev

echo Running migrations...
python manage.py migrate

echo Starting server...
python manage.py runserver 127.0.0.1:8000 