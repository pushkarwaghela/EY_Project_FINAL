# core/context_processors.py
from .models import Event, User

def site_data(request):
    context = {
        'site_name': 'Smart College Event System',
        'site_description': 'Modern event and attendance management system',
    }
    
    if request.user.is_authenticated:
        context['unread_notifications'] = request.user.notifications.filter(is_read=False).count()
        
        if request.user.role == 'student':
            # Student-specific stats
            registered_events = request.user.event_registrations.count()
            attended_events = request.user.event_registrations.filter(attended=True).count()
            attendance_rate = (attended_events / registered_events * 100) if registered_events > 0 else 0
            
            context.update({
                'registered_events': registered_events,
                'attended_events': attended_events,
                'attendance_rate': round(attendance_rate, 1)
            })
    
    return context