# views.py - COMPLETE WORKING VERSION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Sum, F, Avg, Max, Min, BooleanField
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import secrets
import base64
import io
import qrcode
from io import BytesIO
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import User, Event, EventRegistration, AttendanceRecord, Notification, Report
from .forms import UserRegistrationForm, UserLoginForm, EventForm, ManualAttendanceForm, ProfileUpdateForm, UserUpdateForm, AttendanceUpdateForm

# ========== UTILITY FUNCTIONS ==========
def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_staff)

def is_student(user):
    return user.is_authenticated and user.role == 'student'

def is_organizer(user):
    return user.is_authenticated and user.role == 'organizer'

# ========== AUTHENTICATION VIEWS ==========
def home(request):
    """Home page view"""
    upcoming_events = Event.objects.filter(
        status__in=['upcoming', 'ongoing'],
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')[:6]
    
    stats = {
        'total_events': Event.objects.count(),
        'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_attendance': AttendanceRecord.objects.count(),
    }
    
    context = {
        'upcoming_events': upcoming_events,
        'stats': stats,
    }
    return render(request, 'home.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Smart College Event System.')
            
            Notification.objects.create(
                user=user,
                notification_type='system',
                title='Welcome!',
                message='Thank you for registering. Start exploring events now!'
            )
            
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Login view with role-based redirection"""
    if request.user.is_authenticated:
        if request.user.role == 'admin' or request.user.is_staff:
            return redirect('admin_dashboard')
        elif request.user.role == 'student':
            return redirect('student_dashboard')
        else:
            return redirect('home')
    
    role = request.GET.get('role', 'student')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_role = request.POST.get('role', role)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user_role and user.role != user_role:
                messages.error(request, f'Please use the {user.get_role_display()} login portal')
                return redirect(f'/login/?role={user.role}')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            if user.role == 'admin' or user.is_staff:
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    context = {
        'role': role,
        'login_title': 'Student Login' if role == 'student' else 'Admin Login'
    }
    return render(request, 'login.html', context)

@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

# ========== DASHBOARD VIEWS ==========
@login_required
def dashboard(request):
    """Main dashboard redirect"""
    if request.user.role == 'admin' or request.user.is_staff:
        return redirect('admin_dashboard')
    elif request.user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('home')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_events = Event.objects.count()
    active_events = Event.objects.filter(status__in=['upcoming', 'ongoing']).count()
    total_students = User.objects.filter(role='student').count()
    total_organizers = User.objects.filter(role='organizer').count()
    today_attendance = AttendanceRecord.objects.filter(marked_at__date=today).count()
    week_attendance = AttendanceRecord.objects.filter(marked_at__date__gte=week_ago).count()
    month_attendance = AttendanceRecord.objects.filter(marked_at__date__gte=month_ago).count()
    pending_registrations = EventRegistration.objects.filter(attended=False).count()
    
    stats = {
        'total_events': total_events,
        'active_events': active_events,
        'total_students': total_students,
        'total_organizers': total_organizers,
        'today_attendance': today_attendance,
        'week_attendance': week_attendance,
        'month_attendance': month_attendance,
        'pending_registrations': pending_registrations,
    }
    
    recent_events = Event.objects.filter(
        status__in=['upcoming', 'ongoing']
    ).order_by('date', 'start_time')[:5]
    
    recent_attendance = AttendanceRecord.objects.select_related(
        'student', 'event'
    ).order_by('-marked_at')[:10]
    
    recent_registrations = EventRegistration.objects.select_related(
        'student', 'event'
    ).order_by('-registration_date')[:10]
    
    event_categories = Event.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'stats': stats,
        'recent_events': recent_events,
        'recent_attendance': recent_attendance,
        'recent_registrations': recent_registrations,
        'event_categories': event_categories,
        'current_time': timezone.now(),
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Student dashboard view"""
    student = request.user
    today = timezone.now().date()
    
    registered_events = EventRegistration.objects.filter(student=student).count()
    attended_events = EventRegistration.objects.filter(student=student, attended=True).count()
    upcoming_registered = EventRegistration.objects.filter(
        student=student,
        event__date__gte=today,
        event__status__in=['upcoming', 'ongoing']
    ).count()
    
    attendance_rate = round((attended_events / registered_events) * 100, 1) if registered_events > 0 else 0
    
    month_ago = today - timedelta(days=30)
    month_attendance = AttendanceRecord.objects.filter(
        student=student,
        marked_at__date__gte=month_ago
    ).count()
    
    stats = {
        'registered_events': registered_events,
        'attended_events': attended_events,
        'upcoming_events': upcoming_registered,
        'attendance_rate': attendance_rate,
        'month_attendance': month_attendance,
    }
    
    upcoming_events = Event.objects.filter(
        registrations__student=student,
        date__gte=today,
        status__in=['upcoming', 'ongoing']
    ).order_by('date', 'start_time').distinct()[:3]
    
    recent_attendance = AttendanceRecord.objects.filter(
        student=student
    ).select_related('event').order_by('-marked_at')[:5]
    
    all_notifications = Notification.objects.filter(user=student).order_by('-created_at')
    unread_count = all_notifications.filter(is_read=False).count()
    
    context = {
        'student': student,
        'stats': stats,
        'upcoming_events': upcoming_events,
        'recent_attendance': recent_attendance,
        'notifications': {
            'count': all_notifications.count(),
            'unread': unread_count,
            'recent': all_notifications[:5]
        },
    }
    return render(request, 'student_dashboard.html', context)

# ========== EVENT VIEWS ==========
@login_required
def events_list(request):
    """List all events with filtering"""
    events = Event.objects.all()
    
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    date = request.GET.get('date')
    sort = request.GET.get('sort', '-date')
    
    if category:
        events = events.filter(category=category)
    if status:
        events = events.filter(status=status)
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(venue__icontains=search)
        )
    if date:
        events = events.filter(date=date)
    
    if request.user.role == 'student':
        events = events.filter(status__in=['upcoming', 'ongoing'])
    
    if sort == 'date':
        events = events.order_by('date', 'start_time')
    elif sort == '-date':
        events = events.order_by('-date', '-start_time')
    elif sort == 'title':
        events = events.order_by('title')
    elif sort == '-participants':
        events = events.order_by('-current_participants')
    else:
        events = events.order_by('-date', '-start_time')
    
    total_events = Event.objects.count()
    upcoming_count = Event.objects.filter(status='upcoming').count()
    ongoing_count = Event.objects.filter(status='ongoing').count()
    total_participants = EventRegistration.objects.count()
    
    if request.user.role == 'student':
        user_registered_count = EventRegistration.objects.filter(
            student=request.user
        ).count()
    else:
        user_registered_count = 0
    
    if request.user.role in ['admin', 'organizer']:
        completed_count = Event.objects.filter(status='completed').count()
        pending_approvals = EventRegistration.objects.filter(attended=False).count()
    else:
        completed_count = 0
        pending_approvals = 0
    
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(events, 12)
    
    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        events_page = paginator.page(1)
    except EmptyPage:
        events_page = paginator.page(paginator.num_pages)
    
    for event in events_page:
        event.is_registered = EventRegistration.objects.filter(
            event=event, student=request.user
        ).exists()
        
        if event.max_participants > 0:
            event.participation_percentage = min(
                (event.current_participants / event.max_participants) * 100, 100
            )
        else:
            event.participation_percentage = 0
        
        if request.user.role == 'student':
            event.user_can_register = (
                not event.is_registered and 
                event.can_register and 
                not event.is_full
            )
        else:
            event.user_can_register = False
        
        event.status_class = f"bg-{event.status}"
        event.category_bg_class = f"bg-gradient-{event.category}"
    
    context = {
        'events': events_page,
        'categories': Event.CATEGORY_CHOICES,
        'statuses': Event.STATUS_CHOICES,
        'total_events': total_events,
        'upcoming_count': upcoming_count,
        'ongoing_count': ongoing_count,
        'total_participants': total_participants,
        'user_registered_count': user_registered_count,
        'completed_count': completed_count,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'events.html', context)

@login_required
def event_detail(request, event_id):
    """Event detail view"""
    event = get_object_or_404(Event, event_id=event_id)
    is_registered = EventRegistration.objects.filter(event=event, student=request.user).exists()
    registration = EventRegistration.objects.filter(event=event, student=request.user).first()
    
    attendees = EventRegistration.objects.filter(event=event, attended=True).select_related('student')
    
    can_edit = (request.user.role == 'admin') or (request.user == event.organizer)
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
        'attendees': attendees,
        'can_edit': can_edit,
    }
    return render(request, 'event_detail.html', context)

@login_required
@user_passes_test(is_admin)
def create_event(request):
    """Create new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            
            if not event.qr_secret:
                event.qr_secret = secrets.token_urlsafe(32)
                event.save()
            
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', event_id=event.event_id)
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': 'Create New Event',
        'submit_text': 'Create Event',
    }
    return render(request, 'crud/event_form.html', context)

@login_required
def register_event(request, event_id):
    """Register for an event"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.user.role != 'student':
        messages.error(request, 'Only students can register for events.')
        return redirect('event_detail', event_id=event_id)
    
    if EventRegistration.objects.filter(event=event, student=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event_id)
    
    if not event.can_register:
        messages.error(request, 'Cannot register for this event.')
        return redirect('event_detail', event_id=event_id)
    
    if event.is_full:
        messages.error(request, 'This event is full. Registration closed.')
        return redirect('event_detail', event_id=event_id)
    
    EventRegistration.objects.create(event=event, student=request.user)
    event.current_participants += 1
    event.save()
    
    Notification.objects.create(
        user=request.user,
        notification_type='event',
        title='Event Registration',
        message=f'You have successfully registered for "{event.title}"',
        related_event=event
    )
    
    messages.success(request, f'Successfully registered for "{event.title}"!')
    return redirect('event_detail', event_id=event_id)

# ========== ATTENDANCE VIEWS ==========
@login_required
def attendance_view(request):
    """Main attendance page - WORKING VERSION"""
    today = timezone.now().date()
    now = timezone.now()
    
    # Get ongoing events
    ongoing_events = Event.objects.filter(
        status='ongoing',
        date=today,
        start_time__lte=now.time(),
        end_time__gte=now.time()
    ).select_related('organizer')
    
    if request.user.role == 'student':
        # Student specific logic
        my_events = Event.objects.filter(
            registrations__student=request.user,
            date=today,
            status__in=['ongoing', 'upcoming']
        ).select_related('organizer').distinct()
        
        for event in my_events:
            event.attendance_marked = AttendanceRecord.objects.filter(
                event=event,
                student=request.user
            ).exists()
            event.registration = EventRegistration.objects.filter(
                event=event,
                student=request.user
            ).first()
            event.can_mark_attendance = (
                event.status == 'ongoing' and 
                not event.attendance_marked and
                event.start_time <= now.time() <= event.end_time and
                event.registration is not None
            )
    else:
        my_events = ongoing_events
    
    # Get recent attendance based on role
    if request.user.role == 'student':
        recent_attendance = AttendanceRecord.objects.filter(
            student=request.user
        ).select_related('event').order_by('-marked_at')[:10]
    elif request.user.role == 'organizer':
        recent_attendance = AttendanceRecord.objects.filter(
            event__organizer=request.user
        ).select_related('event', 'student').order_by('-marked_at')[:10]
    else:
        recent_attendance = AttendanceRecord.objects.select_related(
            'event', 'student'
        ).order_by('-marked_at')[:10]
    
    # Calculate statistics
    if request.user.role == 'student':
        total_attendance = AttendanceRecord.objects.filter(
            student=request.user
        ).count()
        present_count = total_attendance
        on_time_count = AttendanceRecord.objects.filter(
            student=request.user
        ).annotate(
            is_ontime=Q(marked_at__time__lt=F('event__start_time') + timedelta(minutes=15))
        ).filter(is_ontime=True).count()
        
        # Calculate streak
        today = timezone.now().date()
        attendance_dates = AttendanceRecord.objects.filter(
            student=request.user
        ).dates('marked_at', 'day').order_by('-marked_at')
        
        streak_count = 0
        if attendance_dates.exists():
            current_date = today
            for i, att_date in enumerate(attendance_dates):
                if att_date == current_date - timedelta(days=i):
                    streak_count += 1
                else:
                    break
    else:
        total_attendance = AttendanceRecord.objects.count()
        present_count = AttendanceRecord.objects.filter(verified=True).count()
        on_time_count = AttendanceRecord.objects.filter(
            marked_at__time__lt=F('event__start_time') + timedelta(minutes=15)
        ).count()
        streak_count = 0
    
    # Generate QR data for student
    qr_data = None
    if request.user.role == 'student' and request.user.student_id:
        qr_data = {
            'student_id': request.user.student_id,
            'name': request.user.get_full_name() or request.user.username,
            'user_id': str(request.user.id),
            'type': 'student_identity',
            'timestamp': int(timezone.now().timestamp())
        }
    
    context = {
        'ongoing_events': ongoing_events,
        'my_events': my_events,
        'recent_attendance': recent_attendance,
        'total_attendance': total_attendance,
        'present_count': present_count,
        'on_time_count': on_time_count,
        'streak_count': streak_count,
        'qr_data': json.dumps(qr_data) if qr_data else None,
        'is_admin': request.user.role == 'admin',
        'is_student': request.user.role == 'student',
        'is_organizer': request.user.role == 'organizer',
        'today': today,
        'now': now,
    }
    return render(request, 'attendance.html', context)

@login_required
def mark_manual_attendance(request):
    """Handle manual attendance entry"""
    if request.method == 'POST':
        event_code = request.POST.get('event_code')
        student_id = request.POST.get('student_id', '').strip()
        
        if request.user.role == 'admin' and student_id:
            try:
                student = User.objects.get(
                    Q(student_id=student_id) | Q(username=student_id),
                    role='student'
                )
            except User.DoesNotExist:
                messages.error(request, f'Student "{student_id}" not found')
                return redirect('attendance')
        else:
            student = request.user
        
        try:
            event = Event.objects.get(event_id=event_code)
            
            current_time = timezone.now().time()
            today = timezone.now().date()
            
            is_active = (
                event.status == 'ongoing' and 
                event.date == today and
                event.start_time <= current_time <= event.end_time
            )
            
            if not is_active:
                messages.error(request, 'Event not active for attendance')
                return redirect('attendance')
            
            registration = EventRegistration.objects.get(
                event=event,
                student=student
            )
            
            if AttendanceRecord.objects.filter(event=event, student=student).exists():
                messages.warning(request, 'Attendance already marked')
                return redirect('attendance')
            
            attendance = AttendanceRecord.objects.create(
                event=event,
                student=student,
                registration=registration,
                method='manual',
                device_info=request.META.get('HTTP_USER_AGENT', 'Unknown')[:200],
                verified=True
            )
            
            registration.attended = True
            registration.attendance_time = timezone.now()
            registration.save()
            
            Notification.objects.create(
                user=student,
                notification_type='attendance',
                title='Attendance Marked',
                message=f'Your attendance has been marked for "{event.title}"',
                related_event=event
            )
            
            if request.user.role == 'admin' and request.user != student:
                Notification.objects.create(
                    user=event.organizer,
                    notification_type='event',
                    title='Manual Attendance',
                    message=f'{request.user.get_full_name()} marked attendance for {student.get_full_name()} in "{event.title}"',
                    related_event=event
                )
                messages.success(request, f'Attendance marked for {student.get_full_name()}')
            else:
                messages.success(request, 'Attendance marked successfully!')
            
        except Event.DoesNotExist:
            messages.error(request, 'Event not found')
        except EventRegistration.DoesNotExist:
            messages.error(request, 'Student not registered for this event')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('attendance')

@login_required
def mark_qr_attendance(request):
    """Handle QR code attendance marking"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            
            if not qr_data:
                return JsonResponse({'success': False, 'message': 'No QR data provided'})
            
            try:
                # Try event ID directly
                event = Event.objects.get(event_id=qr_data)
            except Event.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid QR code'})
            
            # Check if user is a student
            if request.user.role != 'student':
                return JsonResponse({
                    'success': False, 
                    'message': 'Only students can mark attendance via QR'
                })
            
            current_time = timezone.now().time()
            today = timezone.now().date()
            
            # Check if event is active
            is_active = (
                event.status == 'ongoing' and 
                event.date == today and
                event.start_time <= current_time <= event.end_time
            )
            
            if not is_active:
                return JsonResponse({
                    'success': False, 
                    'message': 'Event is not active for attendance'
                })
            
            # Check if student is registered
            try:
                registration = EventRegistration.objects.get(
                    event=event,
                    student=request.user
                )
            except EventRegistration.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'You are not registered for this event'
                })
            
            # Check if attendance already marked
            if AttendanceRecord.objects.filter(event=event, student=request.user).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Attendance already marked for this event'
                })
            
            # Mark attendance
            attendance = AttendanceRecord.objects.create(
                event=event,
                student=request.user,
                registration=registration,
                method='qr',
                device_info=request.META.get('HTTP_USER_AGENT', 'Unknown')[:200],
                verified=True
            )
            
            # Update registration
            registration.attended = True
            registration.attendance_time = timezone.now()
            registration.save()
            
            # Send notifications
            Notification.objects.create(
                user=request.user,
                notification_type='attendance',
                title='Attendance Marked',
                message=f'Your attendance has been marked for "{event.title}"',
                related_event=event
            )
            
            if event.organizer and event.organizer != request.user:
                Notification.objects.create(
                    user=event.organizer,
                    notification_type='event',
                    title='Attendance Recorded',
                    message=f'{request.user.get_full_name()} marked attendance for "{event.title}"',
                    related_event=event
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Attendance marked successfully!',
                'data': {
                    'event': event.title,
                    'time': attendance.marked_at.strftime('%I:%M %p'),
                    'date': attendance.marked_at.strftime('%B %d, %Y'),
                    'method': attendance.get_method_display(),
                    'status': attendance.status,
                    'attendance_id': attendance.attendance_id
                }
            })
            
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or expired QR code'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def quick_manual_attendance(request):
    """Quick manual attendance for students"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            event_code = data.get('event_code', '').strip()
            
            if not event_code:
                return JsonResponse({'success': False, 'message': 'Event code is required'})
            
            if request.user.role != 'student':
                return JsonResponse({
                    'success': False, 
                    'message': 'Only students can use this feature'
                })
            
            try:
                event = Event.objects.get(event_id=event_code)
            except Event.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Event not found'})
            
            # Check if event is active
            current_time = timezone.now().time()
            today = timezone.now().date()
            
            is_active = (
                event.status == 'ongoing' and 
                event.date == today and
                event.start_time <= current_time <= event.end_time
            )
            
            if not is_active:
                return JsonResponse({
                    'success': False, 
                    'message': 'Event is not active for attendance'
                })
            
            # Check if student is registered
            try:
                registration = EventRegistration.objects.get(
                    event=event,
                    student=request.user
                )
            except EventRegistration.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'You are not registered for this event'
                })
            
            # Check if attendance already marked
            if AttendanceRecord.objects.filter(event=event, student=request.user).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Attendance already marked for this event'
                })
            
            # Mark attendance
            attendance = AttendanceRecord.objects.create(
                event=event,
                student=request.user,
                registration=registration,
                method='manual',
                device_info=request.META.get('HTTP_USER_AGENT', 'Unknown')[:200],
                verified=True
            )
            
            registration.attended = True
            registration.attendance_time = timezone.now()
            registration.save()
            
            # Send notification
            Notification.objects.create(
                user=request.user,
                notification_type='attendance',
                title='Attendance Marked',
                message=f'Your attendance has been marked for "{event.title}"',
                related_event=event
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Attendance marked successfully!',
                'data': {
                    'event': event.title,
                    'time': attendance.marked_at.strftime('%I:%M %p'),
                    'date': attendance.marked_at.strftime('%B %d, %Y'),
                    'method': 'Manual Entry',
                    'attendance_id': attendance.attendance_id
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid request data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def generate_personal_qr(request):
    """Generate personal QR code for student - FIXED VERSION"""
    # Allow both GET and POST requests
    if request.method in ['GET', 'POST'] and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Only for students
            if request.user.role != 'student':
                return JsonResponse({
                    'success': False, 
                    'message': 'Only students can generate personal QR codes'
                })
            
            student_data = {
                'student_id': request.user.student_id or str(request.user.id),
                'name': request.user.get_full_name() or request.user.username,
                'user_id': str(request.user.id),
                'timestamp': int(timezone.now().timestamp()),
                'type': 'student_identity'
            }
            
            # Generate QR code
            import qrcode
            from io import BytesIO
            import base64
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(student_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return JsonResponse({
                'success': True,
                'qr_code': f"data:image/png;base64,{qr_base64}",
                'student_data': student_data
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def attendance_details(request, attendance_id):
    """Get detailed attendance information"""
    try:
        attendance = AttendanceRecord.objects.get(attendance_id=attendance_id)
        
        if not (request.user.role in ['admin', 'organizer'] or attendance.student == request.user):
            return JsonResponse({'success': False, 'message': 'Permission denied'})
        
        data = {
            'success': True,
            'event': {
                'title': attendance.event.title,
                'venue': attendance.event.venue,
                'date': attendance.event.date.strftime('%B %d, %Y'),
                'time': f"{attendance.event.start_time.strftime('%I:%M %p')} - {attendance.event.end_time.strftime('%I:%M %p')}"
            },
            'student': {
                'name': attendance.student.get_full_name() or attendance.student.username,
                'id': attendance.student.student_id,
                'email': attendance.student.email
            },
            'attendance': {
                'marked_at': attendance.marked_at.strftime('%B %d, %Y %I:%M %p'),
                'method': attendance.get_method_display(),
                'status': attendance.status,
                'status_color': attendance.status_color,
                'verified': attendance.verified,
                'device_info': attendance.device_info
            }
        }
        
        if attendance.latitude and attendance.longitude:
            data['location'] = {
                'latitude': float(attendance.latitude),
                'longitude': float(attendance.longitude)
            }
        
        return JsonResponse(data)
        
    except AttendanceRecord.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Attendance record not found'})

@login_required
def attendance_history(request):
    """Return attendance history for modal"""
    student = request.user
    attendance_records = AttendanceRecord.objects.filter(
        student=student
    ).select_related('event').order_by('-marked_at')
    
    from collections import defaultdict
    monthly_data = defaultdict(list)
    
    for record in attendance_records:
        month_year = record.marked_at.strftime('%B %Y')
        monthly_data[month_year].append(record)
    
    context = {
        'attendance_records': attendance_records,
        'monthly_data': dict(monthly_data),
        'total_count': attendance_records.count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'student/attendance_history.html', context)
    
    return render(request, 'student/attendance_history.html', context)

@login_required
@user_passes_test(is_student)
def generate_certificate(request, attendance_id):
    """Generate attendance certificate PDF"""
    try:
        attendance = AttendanceRecord.objects.get(attendance_id=attendance_id)
        
        # Check permissions
        if not (request.user == attendance.student or request.user.role == 'admin'):
            messages.error(request, 'Permission denied')
            return redirect('attendance')
        
        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Certificate design
        p.setTitle(f"Attendance Certificate - {attendance.event.title}")
        
        # Background
        p.setFillColor(colors.HexColor('#f8f9fa'))
        p.rect(0, 0, width, height, fill=1)
        
        # Header
        p.setFillColor(colors.HexColor('#4361ee'))
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width/2, height - 2*inch, "ATTENDANCE CERTIFICATE")
        
        # Decorative line
        p.setStrokeColor(colors.HexColor('#4361ee'))
        p.setLineWidth(2)
        p.line(1*inch, height - 2.5*inch, width - 1*inch, height - 2.5*inch)
        
        # Certificate text
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 14)
        
        text_lines = [
            "This certifies that",
            f"{attendance.student.get_full_name()}",
            f"({attendance.student.student_id})",
            "",
            f"has successfully attended the event",
            f"'{attendance.event.title}'",
            "",
            f"on {attendance.event.date} at {attendance.event.venue}",
            f"Attendance marked at: {attendance.marked_at.strftime('%B %d, %Y %I:%M %p')}",
            f"Attendance Method: {attendance.get_method_display()}",
            f"Status: {attendance.status.upper()}",
            "",
            "This certificate is proof of participation in the college event.",
            "",
            "Signed,",
            "",
            f"{attendance.event.organizer.get_full_name()}",
            "Event Organizer"
        ]
        
        y_position = height - 3.5*inch
        for line in text_lines:
            p.drawCentredString(width/2, y_position, line)
            y_position -= 0.25*inch
        
        # Footer
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColor(colors.gray)
        p.drawCentredString(width/2, 0.5*inch, 
                           f"Certificate ID: {attendance.attendance_id} | Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        # Create response
        response = FileResponse(buffer, as_attachment=True, 
                               filename=f"certificate-{attendance.attendance_id}.pdf")
        response['Content-Type'] = 'application/pdf'
        
        return response
        
    except AttendanceRecord.DoesNotExist:
        messages.error(request, 'Attendance record not found')
        return redirect('attendance')
    except Exception as e:
        messages.error(request, f'Error generating certificate: {str(e)}')
        return redirect('attendance')

@login_required
def get_ongoing_events(request):
    """Get ongoing events for attendance page"""
    today = timezone.now().date()
    now = timezone.now()
    
    if request.user.role == 'student':
        # Get events student is registered for
        ongoing_events = Event.objects.filter(
            registrations__student=request.user,
            status='ongoing',
            date=today,
            start_time__lte=now.time(),
            end_time__gte=now.time()
        ).distinct()
    else:
        # Admin/Organizer sees all ongoing events
        ongoing_events = Event.objects.filter(
            status='ongoing',
            date=today,
            start_time__lte=now.time(),
            end_time__gte=now.time()
        )
    
    events_data = []
    for event in ongoing_events:
        events_data.append({
            'id': event.event_id,
            'title': event.title,
            'venue': event.venue,
            'time': f"{event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}",
            'can_mark_attendance': True
        })
    
    return JsonResponse({'success': True, 'events': events_data})

# In views.py, update the get_recent_attendance function
# In views.py - FINAL FIXED VERSION of get_recent_attendance
@login_required
def get_recent_attendance(request):
    """Get recent attendance for AJAX updates - SIMPLIFIED BULLETPROOF VERSION"""
    try:
        # Get attendance records based on user role
        if request.user.role == 'admin':
            recent = AttendanceRecord.objects.select_related(
                'event', 'student'
            ).order_by('-marked_at')[:10]
        elif request.user.role == 'organizer':
            recent = AttendanceRecord.objects.filter(
                event__organizer=request.user
            ).select_related('event', 'student').order_by('-marked_at')[:10]
        else:
            recent = AttendanceRecord.objects.filter(
                student=request.user
            ).select_related('event').order_by('-marked_at')[:10]
        
        attendance_data = []
        for record in recent:
            # SIMPLE datetime handling - no complex comparisons
            marked_at_str = ""
            date_str = ""
            
            if record.marked_at:
                try:
                    # Just get the time and date directly
                    marked_at_str = record.marked_at.strftime('%I:%M %p')
                    date_str = record.marked_at.strftime('%B %d, %Y')
                except:
                    # Fallback if strftime fails
                    marked_at_str = str(record.marked_at.time())[:8]
                    date_str = str(record.marked_at.date())
            
            # Get student info safely
            student_name = record.student.get_full_name() or record.student.username
            student_id = record.student.student_id or str(record.student.id)
            
            attendance_data.append({
                'id': record.attendance_id,
                'student_name': student_name,
                'student_id': student_id,
                'event_title': record.event.title,
                'event_venue': record.event.venue,
                'marked_at': marked_at_str,
                'date': date_str,
                'method': record.get_method_display(),
                'status': record.status,
                'status_color': record.status_color,
                'verified': record.verified
            })
        
        return JsonResponse({
            'success': True,
            'attendance': attendance_data,
            'count': len(attendance_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)[:100],  # Limit error length
            'message': 'Error fetching recent attendance'
        })
        
# ========== MISSING FUNCTIONS FROM URLS ==========
@login_required
@user_passes_test(lambda u: u.role in ['admin', 'organizer'])
def toggle_attendance_verification(request, attendance_id):
    """Toggle attendance verification status"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            attendance = AttendanceRecord.objects.get(attendance_id=attendance_id)
            
            if request.user.role == 'organizer' and attendance.event.organizer != request.user:
                return JsonResponse({'success': False, 'message': 'Permission denied'})
            
            attendance.verified = not attendance.verified
            attendance.save()
            
            if attendance.registration:
                attendance.registration.attended = attendance.verified
                attendance.registration.save()
            
            return JsonResponse({
                'success': True,
                'verified': attendance.verified,
                'message': f'Attendance {"verified" if attendance.verified else "unverified"}'
            })
            
        except AttendanceRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Attendance record not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'organizer'])
def generate_event_qr(request, event_id):
    """Generate QR code for an event"""
    try:
        event = Event.objects.get(event_id=event_id)
        
        if request.user.role == 'organizer' and event.organizer != request.user:
            return JsonResponse({'success': False, 'message': 'Permission denied for this event'})
        
        if not event.qr_secret:
            event.qr_secret = secrets.token_urlsafe(32)
            event.save()
        
        qr_data = f"{event.event_id}|{event.qr_secret}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        Notification.objects.create(
            user=request.user,
            notification_type='system',
            title='QR Code Generated',
            message=f'QR code generated for event: {event.title}',
            related_event=event
        )
        
        return JsonResponse({
            'success': True,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'event': {
                'title': event.title,
                'code': event.event_id,
                'time': f"{event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}"
            }
        })
        
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'organizer'])
def admin_generate_qr(request):
    """Admin QR code generation page"""
    if request.user.role == 'organizer':
        events = Event.objects.filter(organizer=request.user, status__in=['upcoming', 'ongoing'])
    else:
        events = Event.objects.filter(status__in=['upcoming', 'ongoing'])
    
    context = {
        'events': events,
        'recent_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).order_by('-date')[:5]
    }
    return render(request, 'crud/generate_qr.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def attendance_list(request):
    """List all attendance records (admin only)"""
    if not (request.user.role == 'admin' or request.user.is_staff):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    attendance_records = AttendanceRecord.objects.all().select_related('event', 'student').order_by('-marked_at')
    
    # Filters
    event_id = request.GET.get('event')
    student_id = request.GET.get('student')
    method = request.GET.get('method')
    verified = request.GET.get('verified')
    
    if event_id:
        attendance_records = attendance_records.filter(event__event_id=event_id)
    if student_id:
        attendance_records = attendance_records.filter(student__student_id=student_id)
    if method:
        attendance_records = attendance_records.filter(method=method)
    if verified:
        attendance_records = attendance_records.filter(verified=(verified == 'true'))
    
    # Get filter options
    events = Event.objects.all()
    students = User.objects.filter(role='student')
    
    context = {
        'attendance_records': attendance_records,
        'events': events,
        'students': students,
        'methods': AttendanceRecord.METHOD_CHOICES,
    }
    return render(request, 'crud/attendance_list.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def update_attendance(request, attendance_id):
    """Update attendance record (admin only)"""
    attendance = get_object_or_404(AttendanceRecord, attendance_id=attendance_id)
    
    if request.method == 'POST':
        form = AttendanceUpdateForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            
            if attendance.registration:
                attendance.registration.attended = attendance.verified
                attendance.registration.save()
            
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('attendance_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttendanceUpdateForm(instance=attendance)
    
    context = {
        'form': form,
        'attendance': attendance,
        'title': f'Update Attendance Record',
        'submit_text': 'Update Attendance',
    }
    return render(request, 'crud/attendance_form.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def delete_attendance(request, attendance_id):
    """Delete attendance record (admin only)"""
    attendance = get_object_or_404(AttendanceRecord, attendance_id=attendance_id)
    
    if request.method == 'POST':
        if attendance.registration:
            registration = attendance.registration
            registration.attended = False
            registration.save()
        
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully!')
        return redirect('attendance_list')
    
    return render(request, 'crud/attendance_confirm_delete.html', {'attendance': attendance})

# ========== OTHER NECESSARY FUNCTIONS ==========
@login_required
def attendance_stats(request):
    """Get attendance statistics for AJAX updates - FIXED VERSION"""
    if request.user.is_authenticated:
        if request.user.role == 'student':
            # Get actual attendance records count
            total_attendance = AttendanceRecord.objects.filter(
                student=request.user
            ).count()
            
            # Calculate on-time count safely
            from django.db.models import Q, F
            from datetime import timedelta
            
            on_time_count = 0
            try:
                # Get all attendance records for student
                attendances = AttendanceRecord.objects.filter(
                    student=request.user
                ).select_related('event')
                
                for attendance in attendances:
                    if attendance.marked_at and attendance.event.start_time:
                        # Calculate if marked within 15 minutes of start
                        event_start = datetime.combine(
                            attendance.event.date, 
                            attendance.event.start_time
                        )
                        # Make both datetimes naive or aware for comparison
                        marked_at = attendance.marked_at
                        
                        # If marked_at is aware, make it naive for comparison
                        if hasattr(marked_at, 'tzinfo') and marked_at.tzinfo:
                            marked_at = timezone.make_naive(marked_at)
                        
                        time_difference = marked_at - event_start
                        if time_difference <= timedelta(minutes=15):
                            on_time_count += 1
            except:
                # If calculation fails, use simple count
                on_time_count = total_attendance
            
            # Calculate streak
            today = timezone.now().date()
            attendance_dates = AttendanceRecord.objects.filter(
                student=request.user
            ).dates('marked_at', 'day').order_by('-marked_at')
            
            streak_count = 0
            if attendance_dates.exists():
                current_date = today
                for i, att_date in enumerate(attendance_dates):
                    if att_date == current_date - timedelta(days=i):
                        streak_count += 1
                    else:
                        break
            
            return JsonResponse({
                'success': True,
                'total_attendance': total_attendance,
                'present_count': total_attendance,
                'on_time_count': on_time_count,
                'streak_count': streak_count,
                'attendance_rate': 100 if total_attendance > 0 else 0
            })
        else:
            # Admin stats - simplified
            total_attendance = AttendanceRecord.objects.count()
            today_attendance = AttendanceRecord.objects.filter(
                marked_at__date=timezone.now().date()
            ).count()
            
            return JsonResponse({
                'success': True,
                'total_attendance': total_attendance,
                'present_count': today_attendance,
                'on_time_count': total_attendance,  # Simplified for admin
                'streak_count': 0
            })
    
    return JsonResponse({'success': False, 'error': 'Unauthorized'})


@login_required
def test_scan(request):
    """Test QR scan endpoint"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Simulate a successful scan for testing
            event = Event.objects.filter(status='ongoing').first()
            if event:
                # Create test attendance record
                registration, created = EventRegistration.objects.get_or_create(
                    event=event,
                    student=request.user,
                    defaults={'attended': True}
                )
                
                attendance = AttendanceRecord.objects.create(
                    event=event,
                    student=request.user,
                    registration=registration,
                    method='qr',
                    device_info='Test Scan',
                    verified=True
                )
                
                registration.attended = True
                registration.attendance_time = timezone.now()
                registration.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Test attendance marked successfully!',
                    'data': {
                        'event': event.title,
                        'time': attendance.marked_at.strftime('%I:%M %p'),
                        'date': attendance.marked_at.strftime('%B %d, %Y'),
                        'method': 'QR Scan (Test)',
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No ongoing events found for testing'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# ========== PROFILE & OTHER VIEWS ==========
@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    stats = {}
    if request.user.role == 'student':
        try:
            stats['registered_events'] = EventRegistration.objects.filter(student=request.user).count()
            stats['attended_events'] = EventRegistration.objects.filter(student=request.user, attended=True).count()
            if stats['registered_events'] > 0:
                stats['attendance_rate'] = round((stats['attended_events'] / stats['registered_events']) * 100, 1)
            else:
                stats['attendance_rate'] = 0
            stats['notifications'] = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception as e:
            print(f"Error calculating stats: {e}")
            stats = {}
    
    context = {'form': form, 'stats': stats}
    return render(request, 'profile.html', context)

@login_required
def notifications_view(request):
    """Notifications view"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    context = {'notifications': notifications}
    return render(request, 'notifications.html', context)

# ========== REPORTS VIEWS ==========
@login_required
@user_passes_test(is_admin)
def reports_view(request):
    """Reports dashboard"""
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    today_stats = {
        'attendance': AttendanceRecord.objects.filter(marked_at__date=today).count(),
        'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
        'total_students': User.objects.filter(role='student', is_active=True).count(),
    }
    
    overall_stats = {
        'total_attendance': AttendanceRecord.objects.count(),
        'total_events': Event.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
    }
    
    reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')
    
    context = {
        'reports': reports,
        'today': today,
        'today_stats': today_stats,
        'overall_stats': overall_stats,
    }
    return render(request, 'reports.html', context)

@login_required
def report_detail(request, report_id):
    """View report details"""
    report = get_object_or_404(Report, report_id=report_id)
    
    if not (request.user.role == 'admin' or report.generated_by == request.user):
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('reports')
    
    context = {'report': report}
    return render(request, 'report_detail.html', context)

# ========== USER MANAGEMENT ==========
@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def user_list(request):
    """List all users (Admin only)"""
    users = User.objects.all().order_by('-date_joined')
    
    role = request.GET.get('role')
    search = request.GET.get('search')
    
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {'users': users, 'roles': User.ROLE_CHOICES}
    return render(request, 'crud/user_list.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def user_detail(request, user_id):
    """View user details (Admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    stats = {}
    if user.role == 'student':
        stats['registered_events'] = EventRegistration.objects.filter(student=user).count()
        stats['attended_events'] = EventRegistration.objects.filter(student=user, attended=True).count()
        stats['attendance_records'] = AttendanceRecord.objects.filter(student=user).count()
    
    context = {'user_profile': user, 'stats': stats}
    return render(request, 'crud/user_detail.html', context)

# ========== API VIEWS ==========
def get_notifications(request):
    """Get user notifications"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        latest = Notification.objects.filter(user=request.user).order_by('-created_at').first()
        
        return JsonResponse({
            'unread_count': unread_count,
            'latest_notification': {
                'title': latest.title if latest else None,
                'message': latest.message if latest else None,
                'created_at': latest.created_at.isoformat() if latest else None
            }
        })
    return JsonResponse({'unread_count': 0})

def get_attendance_stats(request):
    """Get attendance statistics"""
    if request.user.is_authenticated:
        if request.user.role == 'student':
            attended_events = EventRegistration.objects.filter(
                student=request.user, attended=True
            ).count()
            total_registered = EventRegistration.objects.filter(
                student=request.user
            ).count()
            attendance_rate = round((attended_events / total_registered) * 100, 1) if total_registered > 0 else 0
            
            return JsonResponse({
                'attended_events': attended_events,
                'attendance_rate': attendance_rate,
                'total_registered': total_registered
            })
        else:
            total_attendance = AttendanceRecord.objects.count()
            today_attendance = AttendanceRecord.objects.filter(
                marked_at__date=timezone.now().date()
            ).count()
            
            return JsonResponse({
                'total_attendance': total_attendance,
                'today_attendance': today_attendance
            })
    return JsonResponse({'error': 'Unauthorized'}, status=401)

@csrf_exempt
def analytics_pageview(request):
    """Handle page view analytics"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Page view: {data.get('page')} at {data.get('timestamp')}")
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def analytics_event(request):
    """Handle event tracking"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Event: {data.get('event')} - {data.get('properties')}")
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def event_attendance(request, event_id):
    """View attendance for a specific event"""
    event = get_object_or_404(Event, event_id=event_id)
    
    # Check permissions
    if not (request.user.role == 'admin' or 
            (request.user.role == 'organizer' and event.organizer == request.user)):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    attendance_records = AttendanceRecord.objects.filter(event=event).select_related('student')
    
    # Get attendance summary
    total_registered = EventRegistration.objects.filter(event=event).count()
    total_attended = attendance_records.count()
    attendance_rate = round((total_attended / total_registered) * 100, 1) if total_registered > 0 else 0
    
    context = {
        'event': event,
        'attendance_records': attendance_records,
        'total_registered': total_registered,
        'total_attended': total_attended,
        'attendance_rate': attendance_rate,
    }
    return render(request, 'reports/event_attendance.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, notification_id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications')

# ========== OTHER FUNCTIONS ==========
@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def update_event(request, event_id):
    """Update an existing event"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.user != event.organizer and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('event_detail', event_id=event.event_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Update Event: {event.title}',
        'submit_text': 'Update Event',
    }
    return render(request, 'crud/event_form.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def delete_event(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.user != event.organizer and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('events')
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully!')
        return redirect('events')
    
    return render(request, 'crud/event_confirm_delete.html', {'event': event})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def update_user(request, user_id):
    """Update user information (Admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('user_detail', user_id=user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': f'Update User: {user.username}',
        'submit_text': 'Update User',
    }
    return render(request, 'crud/user_form.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def delete_user(request, user_id):
    """Delete a user (Admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'crud/user_confirm_delete.html', {'user': user})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def registration_list(request):
    """List all event registrations (Admin only)"""
    registrations = EventRegistration.objects.all().select_related('event', 'student').order_by('-registration_date')
    
    event_id = request.GET.get('event')
    student_id = request.GET.get('student')
    attended = request.GET.get('attended')
    
    if event_id:
        registrations = registrations.filter(event__event_id=event_id)
    if student_id:
        registrations = registrations.filter(student__student_id=student_id)
    if attended:
        registrations = registrations.filter(attended=(attended == 'true'))
    
    context = {'registrations': registrations}
    return render(request, 'crud/registration_list.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def delete_registration(request, registration_id):
    """Delete event registration (Admin only)"""
    registration = get_object_or_404(EventRegistration, registration_id=registration_id)
    
    if request.method == 'POST':
        event = registration.event
        if event.current_participants > 0:
            event.current_participants -= 1
            event.save()
        
        registration.delete()
        messages.success(request, 'Registration deleted successfully!')
        return redirect('registration_list')
    
    return render(request, 'crud/registration_confirm_delete.html', {'registration': registration})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def toggle_user_active(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_staff)
def toggle_event_status(request, event_id):
    """Toggle event status"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        event = get_object_or_404(Event, event_id=event_id)
        
        status_order = ['draft', 'upcoming', 'ongoing', 'completed', 'cancelled']
        current_index = status_order.index(event.status) if event.status in status_order else 0
        next_index = (current_index + 1) % len(status_order)
        event.status = status_order[next_index]
        event.save()
        
        return JsonResponse({
            'success': True,
            'status': event.status,
            'status_display': event.get_status_display(),
            'message': f'Event status changed to {event.get_status_display()}'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})