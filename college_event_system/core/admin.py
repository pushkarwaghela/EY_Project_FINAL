from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, EventRegistration, AttendanceRecord, Notification, Report

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'student_id', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'student_id')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'role', 'student_id', 'department', 'phone', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'student_id', 'password1', 'password2'),
        }),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_id', 'category', 'date', 'venue', 'organizer', 'status', 'current_participants', 'max_participants')
    list_filter = ('category', 'status', 'date', 'organizer')
    search_fields = ('title', 'event_id', 'venue', 'description')
    readonly_fields = ('event_id', 'qr_secret', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {'fields': ('event_id', 'title', 'description', 'category', 'venue')}),
        ('Timing', {'fields': ('date', 'start_time', 'end_time')}),
        ('Organization', {'fields': ('organizer', 'max_participants', 'current_participants', 'status')}),
        ('QR Code', {'fields': ('qr_code', 'qr_secret')}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('registration_id', 'event', 'student', 'registration_date', 'attended', 'attendance_time')
    list_filter = ('attended', 'registration_date', 'event')
    search_fields = ('registration_id', 'event__title', 'student__username')
    readonly_fields = ('registration_id', 'registration_date')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('attendance_id', 'event', 'student', 'method', 'marked_at', 'verified')
    list_filter = ('method', 'verified', 'marked_at')
    search_fields = ('attendance_id', 'event__title', 'student__username')
    readonly_fields = ('attendance_id', 'marked_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('notification_id', 'created_at')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_by', 'period_start', 'period_end', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title', 'description', 'generated_by__username')
    readonly_fields = ('report_id', 'created_at')