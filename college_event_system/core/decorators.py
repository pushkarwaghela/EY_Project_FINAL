# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.role == 'admin' or request.user.is_staff):
            messages.error(request, 'Admin access required.')
            return redirect('student_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.role != 'student':
            messages.error(request, 'Student access required.')
            return redirect('admin_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, f'Access denied. Required roles: {", ".join(allowed_roles)}')
                
                # Redirect based on current role
                if request.user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('student_dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator