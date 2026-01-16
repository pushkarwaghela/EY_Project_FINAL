# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

class RoleAccessMiddleware:
    """
    Middleware to enforce role-based access control.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for admin panel and static files
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/static/') or 
            request.path.startswith('/media/')):
            return None
        
        # Get current URL name
        try:
            current_url_name = request.resolver_match.url_name
        except:
            current_url_name = None
        
        # Define URL patterns
        ADMIN_URLS = [
            'admin_dashboard', 'create_event', 'update_event', 'delete_event',
            'user_list', 'user_detail', 'update_user', 'delete_user',
            'attendance_list', 'registration_list', 'generate_qr', 'reports',
            'registration_detail', 'report_detail'
        ]
        
        STUDENT_URLS = [
            'student_dashboard', 'register_event', 'attendance_history',
            'mark_qr_attendance'
        ]
        
        PUBLIC_URLS = [
            'home', 'login', 'register', 'logout', 'events', 'event_detail'
        ]
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            user_role = request.user.role
            
            # Admin trying to access student-only pages
            if (user_role == 'admin' or request.user.is_staff) and current_url_name in STUDENT_URLS:
                # Allow access to some student pages
                if current_url_name in ['attendance_history']:
                    return None
                messages.error(request, 'Admin access not allowed for student pages.')
                return redirect('admin_dashboard')
            
            # Student trying to access admin-only pages
            elif user_role == 'student' and current_url_name in ADMIN_URLS:
                messages.error(request, 'Student access not allowed for admin pages.')
                return redirect('student_dashboard')
            
            # Organizer access control
            elif user_role == 'organizer':
                if current_url_name in ['user_list', 'user_detail', 'delete_user']:
                    messages.error(request, 'Organizers cannot manage users.')
                    return redirect('events')
        
        else:
            # Unauthenticated user trying to access protected pages
            if current_url_name not in PUBLIC_URLS:
                messages.info(request, 'Please login to access this page.')
                return redirect(f'{reverse("login")}?next={request.path}')
        
        return None


class UserActivityMiddleware:
    """
    Middleware to track user activity and update last seen.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last activity timestamp
            from .models import User
            User.objects.filter(id=request.user.id).update(
                last_login=timezone.now()
            )
        
        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response