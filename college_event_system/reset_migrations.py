import os
import shutil
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_event_system.settings')
django.setup()

def reset_migrations():
    BASE_DIR = Path(__file__).resolve().parent
    
    # Delete db.sqlite3
    db_file = BASE_DIR / 'db.sqlite3'
    if db_file.exists():
        db_file.unlink()
        print(f"Deleted {db_file}")
    
    # Delete all migration files except __init__.py
    migrations_dir = BASE_DIR / 'core' / 'migrations'
    if migrations_dir.exists():
        for file in migrations_dir.glob('*.py'):
            if file.name != '__init__.py':
                file.unlink()
                print(f"Deleted {file}")
    
    # Also delete pycache folders
    for root, dirs, files in os.walk(BASE_DIR):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_dir = Path(root) / dir_name
                shutil.rmtree(pycache_dir)
                print(f"Deleted {pycache_dir}")
    
    print("\nMigration reset complete!")
    print("\nNow run these commands:")
    print("1. python manage.py makemigrations core")
    print("2. python manage.py migrate")
    print("3. python manage.py createsuperuser")

if __name__ == '__main__':
    reset_migrations()