# urls.py - UPDATED WITH EXISTING FUNCTIONS ONLY
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # ========== ADMIN ==========
    path('admin/', admin.site.urls),
    
    # ========== AUTHENTICATION ==========
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== MAIN PAGES ==========
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # ========== EVENTS ==========
    path('events/', views.events_list, name='events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<str:event_id>/', views.event_detail, name='event_detail'),
    path('events/<str:event_id>/update/', views.update_event, name='update_event'),
    path('events/<str:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<str:event_id>/register/', views.register_event, name='register_event'),
    path('events/<str:event_id>/attendance/', views.event_attendance, name='event_attendance'),
    path('events/<str:event_id>/toggle-status/', views.toggle_event_status, name='toggle_event_status'),
    
    # ========== ATTENDANCE SYSTEM ==========
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/stats/', views.attendance_stats, name='attendance_stats'),
    path('attendance/mark/qr/', views.mark_qr_attendance, name='mark_qr_attendance'),
    path('attendance/mark/manual/', views.mark_manual_attendance, name='mark_manual_attendance'),
    path('attendance/quick-manual/', views.quick_manual_attendance, name='quick_manual_attendance'),
    path('attendance/test-scan/', views.test_scan, name='test_scan'),
    path('attendance/generate-personal-qr/', views.generate_personal_qr, name='generate_personal_qr'),
    path('attendance/details/<str:attendance_id>/', views.attendance_details, name='attendance_details'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path('attendance/certificate/<str:attendance_id>/', views.generate_certificate, name='generate_certificate'),
    path('attendance/ongoing-events/', views.get_ongoing_events, name='get_ongoing_events'),
    path('attendance/get-recent/', views.get_recent_attendance, name='get_recent_attendance'),
    
    # ========== ATTENDANCE MANAGEMENT (ADMIN) ==========
    path('manage/attendance/', views.attendance_list, name='attendance_list'),
    path('manage/attendance/toggle-verification/<str:attendance_id>/',views.toggle_attendance_verification, name='toggle_attendance_verification'),
    path('manage/attendance/update/<str:attendance_id>/',views.update_attendance, name='update_attendance'),
    path('manage/attendance/delete/<str:attendance_id>/',views.delete_attendance, name='delete_attendance'),
    path('generate-qr/', views.admin_generate_qr_page, name='generate_qr'),  # ADD THIS LINE
    path('generate-qr/<int:event_id>/', views.generate_qr_code, name='generate_qr_code'),
    
    # ========== REPORTS ==========
    path('reports/', views.reports_view, name='reports'),
    path('reports/<str:report_id>/', views.report_detail, name='report_detail'),
    
    # ========== PROFILE & NOTIFICATIONS ==========
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<str:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # ========== USER MANAGEMENT ==========
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    
    # ========== REGISTRATION MANAGEMENT ==========
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/<str:registration_id>/delete/', views.delete_registration, name='delete_registration'),
    
    # ========== PASSWORD MANAGEMENT ==========
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='password_change.html'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'
    ), name='password_change_done'),
    
    # ========== API ENDPOINTS ==========
    path('api/analytics/pageview/', csrf_exempt(views.analytics_pageview), name='analytics_pageview'),
    path('api/analytics/event/', csrf_exempt(views.analytics_event), name='analytics_event'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/attendance/stats/', views.get_attendance_stats, name='get_attendance_stats'),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Favicon
from django.views.generic.base import RedirectView
urlpatterns += [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]