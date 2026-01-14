# check_system.py
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_event_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from core.models import Event, User
from django.db import connection

def check_database():
    """Check database connection and tables"""
    print("🔍 Checking database...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection: OK")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    return True

def check_models():
    """Check if models can be created"""
    print("🔍 Checking models...")
    try:
        User = get_user_model()
        print(f"✅ User model: OK (Total users: {User.objects.count()})")
        
        # Check Event model
        event_count = Event.objects.count()
        print(f"✅ Event model: OK (Total events: {event_count})")
        return True
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def check_urls():
    """Check if URLs resolve correctly"""
    print("🔍 Checking URLs...")
    urls_to_check = [
        ('home', {}),
        ('login', {}),
        ('register', {}),
        ('dashboard', {}),
        ('admin_dashboard', {}),
        ('student_dashboard', {}),
        ('events', {}),
        ('create_event', {}),
    ]
    
    all_good = True
    for url_name, kwargs in urls_to_check:
        try:
            path = reverse(url_name, kwargs=kwargs)
            resolved = resolve(path)
            print(f"✅ {url_name}: {path}")
        except Exception as e:
            print(f"❌ {url_name}: {e}")
            all_good = False
    
    return all_good

def check_static_files():
    """Check static files configuration"""
    print("🔍 Checking static files...")
    from django.conf import settings
    
    print(f"✅ STATIC_URL: {settings.STATIC_URL}")
    print(f"✅ MEDIA_URL: {settings.MEDIA_URL}")
    print(f"✅ DEBUG: {settings.DEBUG}")
    
    # Check if directories exist
    static_dirs = settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else []
    for i, dir_path in enumerate(static_dirs):
        if os.path.exists(dir_path):
            print(f"✅ Static dir {i+1}: {dir_path} (Exists)")
        else:
            print(f"⚠️ Static dir {i+1}: {dir_path} (Missing)")
    
    return True

def create_test_users():
    """Create test users if none exist"""
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("👤 Creating admin user...")
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@college.edu',
            password='admin123',
            role='admin',
            first_name='System',
            last_name='Administrator'
        )
        print(f"✅ Created admin: {admin}")
    
    if not User.objects.filter(username='student').exists():
        print("👤 Creating student user...")
        student = User.objects.create_user(
            username='student',
            email='student@college.edu',
            password='student123',
            role='student',
            first_name='Test',
            last_name='Student',
            student_id='STU001'
        )
        print(f"✅ Created student: {student}")
    
    return True

def check_middleware():
    """Check middleware configuration"""
    print("🔍 Checking middleware...")
    from django.conf import settings
    
    for middleware in settings.MIDDLEWARE:
        print(f"✅ {middleware}")
    
    return True

def main():
    print("=" * 60)
    print("SMART COLLEGE EVENT SYSTEM - HEALTH CHECK")
    print("=" * 60)
    
    checks = [
        ("Database", check_database),
        ("Models", check_models),
        ("URLs", check_urls),
        ("Static Files", check_static_files),
        ("Middleware", check_middleware),
        ("Test Users", create_test_users),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 40)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! System is ready.")
        print("\nQuick Start:")
        print("1. Admin: http://127.0.0.1:8000/login/?role=admin")
        print("   Username: admin, Password: admin123")
        print("2. Student: http://127.0.0.1:8000/login/?role=student")
        print("   Username: student, Password: student123")
    else:
        print("⚠️ SOME CHECKS FAILED. Please fix the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()