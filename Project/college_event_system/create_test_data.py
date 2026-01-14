import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_event_system.settings')
django.setup()

from core.models import User, Event, EventRegistration, AttendanceRecord, Notification
from django.contrib.auth.hashers import make_password

def create_test_data():
    print("Creating test data...")
    
    # Create admin user (if not exists)
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@college.edu',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'password': make_password('admin123')
        }
    )
    if created:
        print(f"Created admin user: {admin_user.username}")
    
    # Create student users
    students = []
    for i in range(1, 11):
        student, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@college.edu',
                'first_name': f'Student{i}',
                'last_name': f'Demo',
                'role': 'student',
                'student_id': f'STU202400{i:02d}',
                'department': random.choice(['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Business Administration']),
                'password': make_password('student123')
            }
        )
        if created:
            students.append(student)
            print(f"Created student: {student.username}")
    
    # Create events
    events_data = [
        {
            'title': 'Tech Fest 2024',
            'description': 'Annual technology festival showcasing innovations, coding competitions, and tech workshops.',
            'category': 'technical',
            'venue': 'Main Auditorium',
            'date': timezone.now().date() + timedelta(days=7),
            'start_time': datetime.strptime('10:00', '%H:%M').time(),
            'end_time': datetime.strptime('17:00', '%H:%M').time(),
            'max_participants': 200,
            'status': 'upcoming',
        },
        {
            'title': 'Career Fair',
            'description': 'Connect with top companies and explore job opportunities. Bring your resume!',
            'category': 'workshop',
            'venue': 'College Ground',
            'date': timezone.now().date() + timedelta(days=3),
            'start_time': datetime.strptime('09:00', '%H:%M').time(),
            'end_time': datetime.strptime('16:00', '%H:%M').time(),
            'max_participants': 150,
            'status': 'upcoming',
        },
        {
            'title': 'Cultural Festival',
            'description': 'Annual cultural celebration with music, dance, drama, and food stalls.',
            'category': 'cultural',
            'venue': 'Open Air Theater',
            'date': timezone.now().date() + timedelta(days=14),
            'start_time': datetime.strptime('16:00', '%H:%M').time(),
            'end_time': datetime.strptime('22:00', '%H:%M').time(),
            'max_participants': 300,
            'status': 'upcoming',
        },
        {
            'title': 'Sports Day',
            'description': 'Annual sports competition with various track and field events.',
            'category': 'sports',
            'venue': 'Sports Complex',
            'date': timezone.now().date() + timedelta(days=10),
            'start_time': datetime.strptime('08:00', '%H:%M').time(),
            'end_time': datetime.strptime('18:00', '%H:%M').time(),
            'max_participants': 250,
            'status': 'upcoming',
        },
        {
            'title': 'AI Workshop',
            'description': 'Hands-on workshop on Artificial Intelligence and Machine Learning.',
            'category': 'technical',
            'venue': 'Computer Lab A-101',
            'date': timezone.now().date() + timedelta(days=2),
            'start_time': datetime.strptime('14:00', '%H:%M').time(),
            'end_time': datetime.strptime('17:00', '%H:%M').time(),
            'max_participants': 50,
            'status': 'ongoing',
        },
    ]
    
    events = []
    for event_data in events_data:
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            defaults={
                **event_data,
                'organizer': admin_user
            }
        )
        if created:
            events.append(event)
            print(f"Created event: {event.title}")
    
    # Create registrations
    for student in students:
        for event in events:
            # Randomly register students to events
            if random.random() > 0.3:  # 70% chance of registration
                reg, created = EventRegistration.objects.get_or_create(
                    event=event,
                    student=student
                )
                if created:
                    event.current_participants += 1
                    event.save()
                    print(f"Registered {student.username} for {event.title}")
    
    # Mark some attendance for past/ongoing events
    for student in students[:8]:  # First 8 students
        for event in events:
            if event.status == 'ongoing' or random.random() > 0.5:
                # Check if registered
                reg = EventRegistration.objects.filter(event=event, student=student).first()
                if reg and not reg.attended:
                    # Mark attendance
                    attendance, created = AttendanceRecord.objects.get_or_create(
                        event=event,
                        student=student,
                        defaults={
                            'method': random.choice(['qr', 'manual']),
                            'verified': True
                        }
                    )
                    if created:
                        reg.attended = True
                        reg.attendance_time = timezone.now() - timedelta(hours=random.randint(1, 24))
                        reg.save()
                        print(f"Marked attendance for {student.username} at {event.title}")
    
    # Create some notifications
    notifications_data = [
        {
            'user': admin_user,
            'notification_type': 'system',
            'title': 'Welcome Admin!',
            'message': 'Your admin account has been set up successfully.',
            'is_read': True,
        },
        {
            'user': admin_user,
            'notification_type': 'event',
            'title': 'New Event Created',
            'message': 'Tech Fest 2024 has been created successfully.',
            'related_event': events[0] if events else None,
        },
    ]
    
    for student in students[:5]:
        notifications_data.append({
            'user': student,
            'notification_type': 'system',
            'title': 'Welcome to College Event System!',
            'message': 'Thank you for registering. Start exploring events now!',
            'is_read': False,
        })
    
    for notif_data in notifications_data:
        Notification.objects.get_or_create(
            user=notif_data['user'],
            title=notif_data['title'],
            defaults=notif_data
        )
    
    print("\n✅ Test data created successfully!")
    print(f"\n📋 Login credentials:")
    print(f"   Admin: username='admin', password='admin123'")
    print(f"   Students: username='student1' to 'student10', password='student123'")
    print(f"\n📊 Statistics:")
    print(f"   Total Users: {User.objects.count()}")
    print(f"   Total Events: {Event.objects.count()}")
    print(f"   Total Registrations: {EventRegistration.objects.count()}")
    print(f"   Total Attendance Records: {AttendanceRecord.objects.count()}")

if __name__ == '__main__':
    create_test_data()