from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
import random
import string

# Helper functions for default values
def generate_event_id():
    return f"EV{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

def generate_registration_id():
    return f"REG{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

def generate_attendance_id():
    return f"ATT{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

def generate_notification_id():
    return f"NOT{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

def generate_report_id():
    return f"REP{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('student', 'Student'),
        ('organizer', 'Event Organizer'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['-date_joined']

# Event Model
class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    CATEGORY_CHOICES = (
        ('technical', 'Technical'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('other', 'Other'),
    )
    
    event_id = models.CharField(max_length=20, unique=True, default=generate_event_id)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_participants = models.IntegerField(default=100)
    current_participants = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_secret = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def can_register(self):
        try:
            from django.utils import timezone
            return (self.status in ['upcoming', 'ongoing'] and 
                not self.is_full and 
                self.date >= timezone.now().date())
        except:
            return False
        
    @property
    def icon(self):
        """Return icon based on category"""
        icons = {
            'technical': 'code',
            'cultural': 'music',
            'sports': 'running',
            'workshop': 'chalkboard-teacher',
            'seminar': 'graduation-cap',
            'conference': 'users',
            'other': 'calendar'
        }
        return icons.get(self.category, 'calendar')
    
    @property
    def is_active_for_attendance(self):
        """Check if event is active for attendance marking"""
        from django.utils import timezone
        current_time = timezone.now().time()
        today = timezone.now().date()
        
        return (self.status == 'ongoing' and 
                self.date == today and
                self.start_time <= current_time <= self.end_time)
        
        
        
    

# Event Registration Model
class EventRegistration(models.Model):
    registration_id = models.CharField(max_length=20, unique=True, default=generate_registration_id)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    attendance_time = models.DateTimeField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title}"

# Attendance Record Model
class AttendanceRecord(models.Model):
    METHOD_CHOICES = (
        ('qr', 'QR Scan'),
        ('manual', 'Manual Entry'),
        ('face', 'Face Recognition'),
        ('nfc', 'NFC/RFID'),
    )
    
    attendance_id = models.CharField(max_length=20, unique=True, default=generate_attendance_id)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, related_name='attendance')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='qr')
    marked_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    device_info = models.CharField(max_length=200, blank=True)
    verified = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-marked_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title} - {self.marked_at}"
    

    
    @property
    def status_color(self):
        colors = {
            'on_time': 'success',
            'late': 'warning',
            'absent': 'danger',
            'unknown': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
    @property
    def status_icon(self):
        icons = {
            'on_time': 'check-circle',
            'late': 'clock',
            'absent': 'times-circle',
            'unknown': 'question-circle'
        }
        return icons.get(self.status, 'question-circle')
    
    @property
    def method_icon(self):
        icons = {
            'qr': 'qrcode',
            'manual': 'keyboard',
            'face': 'user-circle',
            'nfc': 'credit-card'
        }
        return icons.get(self.method, 'question-circle')
    
    @property
    def is_verified(self):
        """Check if attendance is verified"""
        return self.verified
    
    @property
    def can_be_verified_by(self, user):
        """Check if user can verify this attendance"""
        if user.role == 'admin':
            return True
        elif user.role == 'organizer' and self.event.organizer == user:
            return True
        return False
    
    def mark_as_verified(self, user):
        """Mark attendance as verified by user"""
        if self.can_be_verified_by(user):
            self.verified = True
            self.save()
            return True
        return False

# Notification Model
class Notification(models.Model):
    TYPE_CHOICES = (
        ('event', 'Event Update'),
        ('attendance', 'Attendance'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
    )
    
    notification_id = models.CharField(max_length=20, unique=True, default=generate_notification_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

# Report Model
class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('attendance', 'Attendance Report'),
        ('event', 'Event Report'),
        ('student', 'Student Report'),
        ('department', 'Department Report'),
    )
    
    report_id = models.CharField(max_length=20, unique=True, default=generate_report_id)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    period_start = models.DateField()
    period_end = models.DateField()
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    data = models.JSONField(default=dict)  # Store report data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.date()}"