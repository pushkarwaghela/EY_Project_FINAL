import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_event_system.college_event_system.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")