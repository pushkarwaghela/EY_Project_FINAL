@echo off
echo 🚀 Starting Smart College Event System...
echo ==========================================

REM Check Python
python --version

REM Make migrations
echo 📦 Checking for migrations...
python manage.py makemigrations

REM Apply migrations
echo 🔄 Applying migrations...
python manage.py migrate

REM Create superuser
echo 👤 Checking for admin user...
python -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating admin user...')
    User.objects.create_superuser('admin', 'admin@college.edu', 'admin123')
    print('✅ Admin user created')
else:
    print('✅ Admin user exists')
"

REM Start server
echo 🌐 Starting development server...
echo ==========================================
echo Admin:     http://127.0.0.1:8000/login/?role=admin
echo            Username: admin, Password: admin123
echo Student:   http://127.0.0.1:8000/login/?role=student
echo            Username: student, Password: student123
echo ==========================================

python manage.py runserver