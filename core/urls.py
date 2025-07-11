from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),

    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/certificates/', views.student_certificates, name='student_certificates'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/progress/', views.student_progress, name='student_progress'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/discussion/', views.student_discussion, name='student_discussion'),

    # Teacher
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/student/', views.teacher_student, name='teacher_student'),
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/library/', views.teacher_library, name='teacher_library'),
    path('teacher/discussion/', views.teacher_discussion, name='teacher_discussion'),
    path('teacher/liveclasses/', views.teacher_liveclasses, name='teacher_liveclasses'),
    path('teacher/settings/', views.teacher_settings, name='teacher_settings'),
    path('teacher/progress/', views.teacher_progress, name='teacher_progress'),

    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/assignments/', views.admin_assignments, name='admin_assignments'),
    path('admin/profile/', views.admin_profile, name='admin_profile'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
]