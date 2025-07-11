from django.shortcuts import render

# 🏠 Public
def index(request):
    return render(request, 'core/index.html')

# 🔐 Auth
def login_view(request):
    return render(request, 'core/auth/login.html')

def signup_view(request):
    return render(request, 'core/auth/signup.html')

# 👨‍🎓 Student Views
def student_dashboard(request):
    return render(request, 'core/student/student_dashboard.html')

def student_courses(request):
    return render(request, 'core/student/student_courses.html')

def student_assignments(request):
    return render(request, 'core/student/student_assignments.html')

def student_certificates(request):
    return render(request, 'core/student/student_certificates.html')

def student_profile(request):
    return render(request, 'core/student/student_profile.html')

def student_progress(request):
    return render(request, 'core/student/student_progress.html')

def student_schedule(request):
    return render(request, 'core/student/student_schedule.html')

def student_discussion(request):
    return render(request, 'core/student/student_discussion.html')

# 👨‍🏫 Teacher Views
def teacher_dashboard(request):
    return render(request, 'core/teacher/teachers_dashboard.html')

def teacher_courses(request):
    return render(request, 'core/teacher/teacher_courses.html')

def teacher_assignments(request):
    return render(request, 'core/teacher/teacher_assignments.html')

def teacher_student(request):
    return render(request, 'core/teacher/teacher_student.html')

def teacher_schedule(request):
    return render(request, 'templates/core/teacher/teacher_schedule.html')

def teacher_library(request):
    return render(request, 'core/teacher/teacher_library.html')

def teacher_discussion(request):
    return render(request, 'core/teacher/teacher_discussion.html')

def teacher_liveclasses(request):
    return render(request, 'core/teacher/teacher_liveclasses.html')

def teacher_settings(request):
    return render(request, 'core/teacher/teacher_settings.html')

def teacher_progress(request):
    return render(request, 'core/teacher/teracher_progress.html')

# 🧑‍💼 Admin Views
def admin_dashboard(request):
    return render(request, 'core/admin/admin_dashboard.html')

def admin_courses(request):
    return render(request, 'core/admin/admin_courses.html')

def admin_assignments(request):
    return render(request, 'core/admin/admin_assignments.html')

def admin_profile(request):
    return render(request, 'core/admin/admin_profile.html')

def admin_settings(request):
    return render(request, 'core/admin/admin_settings.html')

def admin_users(request):
    return render(request, 'core/admin/admin_users.html')

def admin_reports(request):
    return render(request, 'core/admin/admin_reports.html')