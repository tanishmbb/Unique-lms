# core/views.py

from datetime import datetime
import csv
import json
from logging import Manager
import openpyxl

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from .utils import redirect_with_tab

from .forms import (
    AddStudentForm,
    AccountForm,
    LibraryContentForm,
    NotificationForm,
    PreferencesForm,
    PushNotificationForm,
    ScheduleEventForm,
    TeacherSecurityForm,
    UploadExcelForm,
    CustomUserCreationForm,
    TeacherProfileForm,
    DiscussionPostForm,
    Discussion,
    DiscussionForm
)

from .models import (
    Assignment,
    Course,
    CourseCategory,
    CustomUser,
    Discussion,
    DiscussionReply,
    LibraryContent,
    LiveClass,
    ScheduleEvent,
    Student,
    Submission,
    Teacher,
    TeachingPreferences,
    NotificationSettings,
    PushNotificationSettings,
)



# ------------------- auth Views -------------------
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


from django.db import IntegrityError

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import CustomUser, Teacher, Manager, Student
from django.contrib.auth import logout

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


def signup_view(request):
    if request.user.is_authenticated:
        # Redirect logged-in users based on role
        if request.user.role == CustomUser.Role.TEACHER:
            return redirect("teacher_dashboard")
        elif request.user.role == CustomUser.Role.MANAGER:
            return redirect("manager_dashboard")
        elif request.user.role == CustomUser.Role.STUDENT:
            return redirect("student_dashboard")
        else:
            return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["role"] == CustomUser.Role.STUDENT:
                messages.error(request, "Student registration is not allowed.")
                return render(request, "core/auth/signup.html", {"form": form})

            user = form.save()
            login(request, user)

            # Create related profile model based on role
            if user.role == CustomUser.Role.TEACHER:
                Teacher.objects.create(user=user)
                return redirect("teacher_dashboard")
            elif user.role == CustomUser.Role.MANAGER:
                Manager.objects.create(user=user)
                return redirect("manager_dashboard")
            elif user.role == CustomUser.Role.STUDENT:
                Student.objects.create(user=user)
                return redirect("student_dashboard")

            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "core/auth/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "core/auth/login.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.role == CustomUser.Role.TEACHER:
            return reverse("teacher_dashboard")
        elif user.role == CustomUser.Role.MANAGER:
            return reverse("manager_dashboard")
        elif user.role == CustomUser.Role.STUDENT:
            return reverse("student_dashboard")
        else:
            return reverse("home")


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required




# ------------------- Teacher Views -------------------
def index(request):
    return render(request, "core/index.html")


@login_required
def get_submissions(request, assignment_id):
    assignment = get_object_or_404(
        Assignment, id=assignment_id, course__instructor=request.user
    )
    submissions = assignment.submissions.select_related("student").all()

    data = []
    for submission in submissions:
        data.append(
            {
                "student": submission.student.get_full_name(),
                "email": submission.student.email,
                "submitted_at": submission.submitted_at.strftime("%Y-%m-%d %H:%M"),
                "grade": submission.grade,
                "status": submission.status,
            }
        )

    # You might want to return JsonResponse(data), but redirecting here
    return redirect("teacher_assignments")


@login_required
def view_student_profile(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    return render(
        request, "core/teacher/view_student_profile.html", {"student": student}
    )


@login_required
def message_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            # TODO: Implement message saving logic here
            messages.success(request, f"Message sent to {student.get_full_name()}.")
            return redirect("teacher_students")
        else:
            messages.error(request, "Message cannot be empty.")
    return render(request, "core/teacher/message_student.html", {"student": student})


@login_required
def deactivate_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    if student.is_active:
        student.is_active = False
        student.save()
        messages.success(request, f"{student.get_full_name()} deactivated.")
    else:
        messages.info(request, f"{student.get_full_name()} is already inactive.")
    return redirect("teacher_students")


@login_required
def activate_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    if not student.is_active:
        student.is_active = True
        student.save()
        messages.success(request, f"{student.get_full_name()} activated.")
    else:
        messages.info(request, f"{student.get_full_name()} is already active.")
    return redirect("teacher_students")


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .models import Discussion, DiscussionReply, Course

@login_required
def teacher_discussions(request):
    user = request.user
    teacher = getattr(user, 'teacher_profile', None)
    if not teacher:
        return redirect('index')

    courses = Course.objects.filter(instructor=teacher)

    filter_course = request.GET.get('course', 'all')
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    discussions = Discussion.objects.all()

    # Filter by course
    if filter_course != 'all':
        if filter_course == 'none':
            discussions = discussions.filter(course__isnull=True)
        else:
            discussions = discussions.filter(course_id=filter_course)

    # Filter by status
    if filter_status != 'all':
        discussions = discussions.filter(status=filter_status)

    # Search filter (title/content)
    if search_query:
        discussions = discussions.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Order pinned first, then recent
    discussions = discussions.order_by('-pinned', '-created_at')

    paginator = Paginator(discussions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats
    active_discussions_count = Discussion.objects.filter(status='active').count()
    total_replies = DiscussionReply.objects.count()
    total_discussions = Discussion.objects.count()
    discussions_with_replies = Discussion.objects.annotate(reply_count=Count('replies')).filter(reply_count__gt=0).count()
    response_rate = round((discussions_with_replies / total_discussions * 100), 2) if total_discussions else 0

    context = {
        'courses': courses,
        'discussions': page_obj,
        'filter_course': filter_course,
        'filter_status': filter_status,
        'search_query': search_query,
        'active_discussions_count': active_discussions_count,
        'total_replies': total_replies,
        'response_rate': response_rate,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'core/teacher/teacher_discussion.html', context)


@login_required
def create_discussion(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        course_id = request.POST.get("course")
        pinned = request.POST.get("pinned") == "on"

        course = None
        if course_id and course_id != "none":
            course = Course.objects.filter(id=course_id).first()

        Discussion.objects.create(
            title=title,
            content=content,
            course=course,
            creator=request.user,
            pinned=pinned,
            status="active",
        )
        return redirect("teacher_discussions")
    else:
        return redirect("teacher_discussions")


@login_required
def content_library(request):
    teacher = request.user
    courses = Course.objects.filter(instructor=teacher)

    course_id = request.GET.get("course")
    search = request.GET.get("search", "").strip()

    contents = LibraryContent.objects.filter(uploaded_by=teacher)

    if course_id:
        contents = contents.filter(course_id=course_id)

    if search:
        contents = contents.filter(title__icontains=search)

    contents = contents.order_by("-uploaded_at")

    paginator = Paginator(contents, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        form = LibraryContentForm(request.POST, request.FILES)
        if form.is_valid():
            new_content = form.save(commit=False)
            new_content.uploaded_by = teacher
            # Optionally, you can detect file_type based on uploaded file
            new_content.file_type = "document"  # Example placeholder
            new_content.save()
            messages.success(request, "Content uploaded successfully.")
            return redirect("content_library")
    else:
        form = LibraryContentForm()

    context = {
        "courses": courses,
        "contents": page_obj,
        "form": form,
        "page_obj": page_obj,
    }
    return render(request, "core/teacher/teacher_library.html", context)


def redirect_with_tab(viewname, tab):
    url = reverse(viewname)
    return redirect(f"{url}?tab={tab}")


from .forms import (
    TeacherProfileForm,
    AccountForm,
    TeacherSecurityForm,
    NotificationForm,
    PushNotificationForm,
    PreferencesForm,
)


@login_required
def teacher_settings(request):
    user = request.user
    tab = request.POST.get("tab") or request.GET.get("tab") or "profile"

    # Correctly instantiate forms with their classes
    profile_form = TeacherProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=getattr(user, "teacher_profile", None),
    )
    account_form = AccountForm(request.POST or None, instance=user)
    password_form = TeacherSecurityForm(request.POST or None)
    notifications_form = NotificationForm(
        request.POST or None, instance=getattr(user, "notification_settings", None)
    )
    push_notifications_form = PushNotificationForm(
        request.POST or None, instance=getattr(user, "push_notification_settings", None)
    )
    preferences_form = PreferencesForm(
        request.POST or None, instance=getattr(user, "teaching_preferences", None)
    )

    if request.method == "POST":
        if tab == "profile" and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect_with_tab("teacher_settings", tab)

        elif tab == "account" and account_form.is_valid():
            account_form.save()
            messages.success(request, "Account settings saved.")
            return redirect_with_tab("teacher_settings", tab)

        elif tab == "security" and password_form.is_valid():
            # Custom logic since TeacherSecurityForm is not a built-in password form
            current_password = password_form.cleaned_data.get("current_password")
            new_password = password_form.cleaned_data.get("new_password")

            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect_with_tab("teacher_settings", tab)
            else:
                password_form.add_error(
                    "current_password", "Incorrect current password."
                )

        elif tab == "notifications" and notifications_form.is_valid():
            notifications_form.save()
            messages.success(request, "Notification preferences saved.")
            return redirect_with_tab("teacher_settings", tab)

        elif tab == "push_notifications" and push_notifications_form.is_valid():
            push_notifications_form.save()
            messages.success(request, "Push notification preferences saved.")
            return redirect_with_tab("teacher_settings", tab)

        elif tab == "preferences" and preferences_form.is_valid():
            preferences_form.save()
            messages.success(request, "Preferences saved.")
            return redirect_with_tab("teacher_settings", tab)

    context = {
        "profile_form": profile_form,
        "account_form": account_form,
        "password_form": password_form,
        "notifications_form": notifications_form,
        "push_notifications_form": push_notifications_form,
        "preferences_form": preferences_form,
        "active_tab": tab,
    }
    return render(request, "core/teacher/teacher_settings.html", context)


@login_required
def teacher_schedule_view(request):
    form = ScheduleEventForm()
    events = ScheduleEvent.objects.filter(instructor=request.user)
    return render(
        request,
        "core/teacher/teacher_schedule.html",
        {
            "form": form,
            "events": events,
        },
    )


@login_required
@require_POST
def add_schedule_event(request):
    form = ScheduleEventForm(request.POST)
    if form.is_valid():
        event = form.save(commit=False)
        event.instructor = request.user
        event.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required
@require_POST
def edit_schedule_event(request, event_id):
    event = get_object_or_404(ScheduleEvent, pk=event_id, instructor=request.user)
    form = ScheduleEventForm(request.POST, instance=event)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required
@require_POST
def delete_schedule_event(request, event_id):
    event = get_object_or_404(ScheduleEvent, pk=event_id, instructor=request.user)
    event.delete()
    return JsonResponse({"success": True})


# Optional combined save endpoint (create or edit)
@login_required
@csrf_exempt  # Consider CSRF protection or AJAX header token in production
def schedule_event_save(request):
    if request.method == "POST":
        user = request.user
        event_id = request.POST.get("id")

        if event_id:
            event = get_object_or_404(ScheduleEvent, pk=event_id, instructor=user)
            form = ScheduleEventForm(request.POST, instance=event)
        else:
            form = ScheduleEventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.instructor = user
            event.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@login_required
def teacher_liveclasses(request):
    if request.user.role != "teacher":
        return redirect("login")

    live_classes = LiveClass.objects.filter(teacher=request.user)
    upcoming_classes = live_classes.filter(start_time__gte=timezone.now())
    past_classes = live_classes.filter(start_time__lt=timezone.now())

    context = {
        "upcoming_classes": upcoming_classes,
        "past_classes": past_classes,
        "courses": Course.objects.filter(instructor=request.user),
    }
    return render(request, "core/teacher/teacher_liveclasses.html", context)


@login_required
@require_POST
def teacher_schedule_class(request):
    title = request.POST.get("classTitle")
    course_id = request.POST.get("classCourse")
    start_time = request.POST.get("startTime")
    duration = request.POST.get("duration")
    platform = request.POST.get("platform")
    description = request.POST.get("classDescription", "")
    is_recorded = bool(request.POST.get("recordClass"))
    repeat_weekly = bool(request.POST.get("repeatWeekly"))

    try:
        duration_minutes = int(duration.replace(" mins", "").strip())
    except (ValueError, AttributeError):
        messages.error(request, "Invalid duration format.")
        return redirect("teacher_liveclasses")

    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
    except Course.DoesNotExist:
        messages.error(request, "Invalid course selected.")
        return redirect("teacher_liveclasses")

    LiveClass.objects.create(
        teacher=request.user,
        course=course,
        title=title,
        description=description,
        start_time=start_time,
        duration_minutes=duration_minutes,
        platform=platform,
        meeting_link="#",  # TODO: generate real meeting link
        is_recorded=is_recorded,
        repeat_weekly=repeat_weekly,
    )

    messages.success(request, "Live class scheduled successfully.")
    return redirect("teacher_liveclasses")


# ------------------- Student Views -------------------


from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.shortcuts import render
from django.utils import timezone
from core.models import Course, Assignment, LiveClass, Submission

from django.db.models import Avg
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Q
from core.models import Course, Assignment, Submission, LiveClass

@login_required
def student_dashboard(request):
    user = request.user

    try:
        student = user.student_profile
    except:
        return redirect("index")  # fallback if not a student

    # ✅ Get all courses created by the student's assigned teacher
    teacher = student.assigned_teacher
    if not teacher:
        return render(request, "core/errors/no_teacher.html")

    # ✅ Fetch active courses by this teacher
    active_courses = Course.objects.filter(
        instructor=teacher,
        status="active"
    ).select_related("instructor", "category")

    # ✅ Pending assignments not submitted
    pending_assignments = Assignment.objects.filter(
        course__in=active_courses,
        status="active"
    ).exclude(
        submissions__student=student,
        submissions__status="completed"
    )

    # ✅ Upcoming live classes
    now = timezone.now()
    upcoming_live_classes = LiveClass.objects.filter(
        course__in=active_courses,
        start_time__gte=now
    )

    # ✅ Average grade across submissions
    avg_grade_agg = Submission.objects.filter(
        student=student,
        grade__isnull=False
    ).aggregate(avg_grade=Avg("grade"))
    average_grade = round(avg_grade_agg["avg_grade"], 2) if avg_grade_agg["avg_grade"] else "N/A"

    # ✅ Per-course data
    course_data = []
    for course in active_courses:
        total_assignments = course.assignments.filter(status="active").count()
        completed_assignments = course.assignments.filter(
            status="active",
            submissions__student=student,
            submissions__status="completed"
        ).distinct().count()

        progress = int((completed_assignments / total_assignments) * 100) if total_assignments else 0
        new_assignments_count = total_assignments - completed_assignments

        course_data.append({
            "id": course.id,
            "title": course.title,
            "category": course.category.name if course.category else "General",
            "instructor": course.instructor.full_name if course.instructor else "Unknown",
            "progress": progress,
            "new_assignments_count": new_assignments_count,
        })

    context = {
        "courses": course_data,
        "pending_assignments_count": pending_assignments.count(),
        "live_classes_count": upcoming_live_classes.count(),
        "average_grade": average_grade,
        "schedule_url": "/student/schedule/",
    }

    return render(request, "core/student/student_dashboard.html", context)


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def student_courses(request):
    user = request.user
    student = user.student_profile
    assigned_teacher = student.assigned_teacher

    if not assigned_teacher:
        courses = Course.objects.none()
    else:
        courses = Course.objects.filter(
            instructor=assigned_teacher,
            status='active'
        ).prefetch_related('assignments')

    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort_by', 'title')

    filtered_courses = []
    for course in courses:
        total_assignments = course.assignments.filter(status='active').count()
        submitted_assignments = course.assignments.filter(
            status='active',
            submissions__student=student
        ).distinct().count()
        progress = int((submitted_assignments / total_assignments) * 100) if total_assignments else 0

        # Filter by status
        if status_filter == 'in_progress' and (progress == 0 or progress == 100):
            continue
        elif status_filter == 'completed' and progress != 100:
            continue
        elif status_filter == 'saved' and progress != 0:
            continue
        elif status_filter not in ('all', 'in_progress', 'completed', 'saved'):
            continue

        if search_query and search_query.lower() not in course.title.lower():
            continue

        # Add badges
        if progress == 100:
            badge_text = "Completed"
            badge_icon = "fa-check-circle"
        elif progress > 0:
            badge_text = "In Progress"
            badge_icon = "fa-spinner"
        else:
            badge_text = "Saved"
            badge_icon = "fa-bookmark"

        # Attach dynamic properties for template
        course.progress = progress
        course.badge_text = badge_text
        course.badge_icon = badge_icon

        filtered_courses.append(course)

    # Sorting
    if sort_by == 'title':
        filtered_courses.sort(key=lambda c: c.title.lower())
    elif sort_by == 'progress':
        filtered_courses.sort(key=lambda c: c.progress, reverse=True)

    # Pagination
    paginator = Paginator(filtered_courses, 6)  # 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'courses': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'status_options': [
            ('all', 'All Courses'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('saved', 'Saved'),
        ],
    }
    return render(request, 'core/student/student_courses.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from core.models import Assignment, Submission, Student
from django.db.models import Count, Avg

@login_required
def student_assignments(request):
    user = request.user

    try:
        student = user.student_profile
    except Student.DoesNotExist:
        return render(request, "core/errors/not_student.html")

    teacher = student.assigned_teacher
    if not teacher:
        return render(request, "core/errors/no_teacher.html")

    # Filters
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "all")
    sort_by = request.GET.get("sort", "due_date")

    # Base queryset: assignments created by teacher
    assignments_qs = Assignment.objects.filter(
        course__instructor=teacher,
        status="active"
    )

    # Search
    if search_query:
        assignments_qs = assignments_qs.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Filter by submission status
    if status_filter == "submitted":
        assignments_qs = assignments_qs.filter(
            submissions__student=student,
            submissions__status="submitted"
        )
    elif status_filter == "graded":
        assignments_qs = assignments_qs.filter(
            submissions__student=student,
            submissions__status="graded"
        )
    elif status_filter == "pending":
        assignments_qs = assignments_qs.exclude(
            submissions__student=student
        )
    # default (all) will not filter

    # Sorting
    if sort_by == "title":
        assignments_qs = assignments_qs.order_by("title")
    elif sort_by == "course":
        assignments_qs = assignments_qs.order_by("course__title")
    else:
        assignments_qs = assignments_qs.order_by("due_date")

    # Annotate each assignment with status
    assignments = []
    for assignment in assignments_qs.select_related("course", "course__instructor"):
        submission = Submission.objects.filter(student=student, assignment=assignment).first()
        item = assignment
        item.status = submission.status if submission else "active"
        item.is_overdue = assignment.due_date < timezone.now() and not submission
        assignments.append(item)

    # Completed assignments
    completed_assignments = Submission.objects.filter(
        student=student
    ).select_related("assignment", "assignment__course")

    context = {
        "assignments": assignments,
        "completed_assignments": completed_assignments,
        "status_tabs": {
            "all": "All",
            "pending": "Pending",
            "submitted": "Submitted",
            "graded": "Graded"
        },
        "sort_tabs": {
            "due_date": "Due Date",
            "title": "Title",
            "course": "Course"
        },
        "status_filter": status_filter,
        "search_query": search_query,
        "today": timezone.now().date()
    }

    return render(request, "core/student/student_assignments.html", context)


@login_required
def submit_assignment(request, assignment_id):
    user = request.user
    student = getattr(user, "student_profile", None)
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("student:assignments")

    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.course.instructor != student.assigned_teacher:
        messages.error(request, "You are not allowed to submit this assignment.")
        return redirect("student:assignments")

    if request.method == "POST":
        submission_file = request.FILES.get("submission_file")
        notes = request.POST.get("notes", "")

        if not submission_file:
            messages.error(request, "Please upload a file to submit.")
            return redirect("student:assignments")

        Submission.objects.update_or_create(
            assignment=assignment,
            student=student,
            defaults={
                "file": submission_file,
                "feedback": notes,
                "status": "submitted",
                "submitted_at": timezone.now(),
            },
        )
        messages.success(request, "Assignment submitted successfully!")
        return redirect("assignments")

    return redirect("assignments")

# @login_required
# def student_schedule(request):
#     user = request.user
#     course_ids = Enrollment.objects.filter(student=user, status="active").values_list(
#         "course_id", flat=True
#     )
#     upcoming_events = ScheduleEvent.objects.filter(
#         course_id__in=course_ids, start_datetime__gte=timezone.now()
#     ).order_by("start_datetime")

#     events_json = json.dumps(
#         [
#             {
#                 "title": f"{event.title} - {event.course.title}",
#                 "start": event.start_datetime.isoformat(),
#                 "end": event.end_datetime.isoformat() if event.end_datetime else None,
#                 "event_type": event.event_type,
#             }
#             for event in upcoming_events
#         ]
#     )

#     context = {
#         "upcoming_events": upcoming_events,
#         "courses": Course.objects.filter(id__in=course_ids),
#         "today": timezone.now().date(),
#         "events_json": events_json,
#     }
#     return render(request, "core/student/student_schedule.html", context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Discussion, Course, CustomUser
from .forms import DiscussionPostForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from core.models import Discussion, Course, DiscussionReply
from core.forms import DiscussionForm

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from core.models import Discussion, Course


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import Course, Discussion

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Discussion, CustomUser, Course

@login_required
def student_discussions(request):
    user = request.user
    if user.role != 'student':
        return redirect('login')

    # Get all teachers
    teachers = CustomUser.objects.filter(role='teacher')

    # Get all courses (optional: all courses or just courses of teachers who posted)
    courses = Course.objects.all()

    # Get discussions created by any teacher
    discussions = Discussion.objects.filter(creator__in=teachers).order_by('-created_at')

    # Search filter
    query = request.GET.get('q', '').strip()
    if query:
        discussions = discussions.filter(Q(title__icontains=query) | Q(content__icontains=query))

    # Pagination
    paginator = Paginator(discussions, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'courses': courses,
        'query': query,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'active_tab': 'all',
    }
    return render(request, 'core/student/student_discussion.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Course, CustomUser, Submission, LiveClass, ScheduleEvent
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Course, Submission, LiveClass, ScheduleEvent, CustomUser

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from core.models import (
    CustomUser,
    Teacher,
    Course,
    Submission,
    LiveClass,
    ScheduleEvent,
)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from core.models import (
    CustomUser, Course, Student, Submission, LiveClass,
    ScheduleEvent, Teacher
)

@login_required
def teacher_dashboard(request):
    user = request.user
    if user.role != CustomUser.Role.TEACHER:
        return redirect("index")

    try:
        teacher = user.teacher_profile
    except Teacher.DoesNotExist:
        return render(request, "core/errors/teacher_profile_not_found.html", status=403)

    # Courses created by this teacher
    courses = Course.objects.filter(instructor=teacher)
    total_courses = courses.count()

    # Students assigned to this teacher
    total_students = Student.objects.filter(assigned_teacher=teacher).count()

    # Submissions needing grading
    pending_grading = Submission.objects.filter(
        assignment__course__in=courses,
        status="submitted"
    ).count()

    now = timezone.now()

    # Upcoming live classes
    live_classes = LiveClass.objects.filter(
        teacher=teacher,
        start_time__gte=now
    ).count()

    # Recent submissions
    recent_submissions = Submission.objects.filter(
        assignment__course__in=courses
    ).select_related("student", "assignment__course").order_by("-submitted_at")[:10]

    # Upcoming schedule events
    upcoming_schedule = ScheduleEvent.objects.filter(
        course__in=courses,
        start_datetime__gte=now
    ).order_by("start_datetime")[:5]

    announcements = []  # Placeholder if announcements are added later

    # Course-level statistics
    course_list = []
    for course in courses:
        total_submissions = Submission.objects.filter(
            assignment__course=course
        ).count()
        graded_submissions = Submission.objects.filter(
            assignment__course=course,
            status="graded"
        ).count()

        progress = int((graded_submissions / total_submissions) * 100) if total_submissions else 0
        modules_count = course.modules.count()
        assignments_count = course.assignments.count()

        # Number of students who are assigned to the teacher (you can also track per-course if needed)
        student_count = Student.objects.filter(assigned_teacher=teacher).count()

        course_list.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "category": course.category.name if course.category else "",
            "progress": progress,
            "students": student_count,
            "modules": modules_count,
            "assignments": assignments_count,
        })

    context = {
        "courses": course_list,
        "total_courses": total_courses,
        "total_students": total_students,
        "pending_grading": pending_grading,
        "live_classes": live_classes,
        "recent_submissions": recent_submissions,
        "upcoming_schedule": upcoming_schedule,
        "announcements": announcements,
    }

    return render(request, "core/teacher/teachers_dashboard.html", context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Course, CourseCategory, Teacher

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, CourseCategory


@login_required
def teacher_courses(request):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    if not teacher:
        # Handle error or redirect - user is not a teacher
        return redirect("index")
    if request.method == "POST":
        # Handle course creation
        title = request.POST.get("title")
        code = request.POST.get("code")
        description = request.POST.get("description")
        level = request.POST.get("level")
        category_id = request.POST.get("category")
        is_draft = request.POST.get("is_draft") == "on"
        thumbnail = request.FILES.get("thumbnail")

        category = get_object_or_404(CourseCategory, id=category_id)

        Course.objects.create(
            title=title,
            code=code,
            description=description,
            level=level,
            category=category,
            instructor=teacher,
            status="draft" if is_draft else "active",
            thumbnail=thumbnail,
        )
        return redirect("teacher_courses")

    # GET request: display courses list
    courses = Course.objects.filter(instructor=teacher, status="active")
    archived_courses = Course.objects.filter(instructor=teacher, status="archived")
    categories = CourseCategory.objects.all()

    context = {
        "courses": courses,
        "archived_courses": archived_courses,
        "categories": categories,
    }
    return render(request, "core/teacher/teacher_courses.html", context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Assignment, Course
from .forms import AssignmentForm  # You may define this


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Assignment, Course
from .forms import AssignmentForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import Assignment, Course
from .forms import AssignmentForm


@login_required
def teacher_assignments(request):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    if not teacher:
        return redirect("index")

    courses = Course.objects.filter(instructor=teacher)
    selected_course = request.GET.get("course")
    search_query = request.GET.get("search")
    selected_assignment_id = request.GET.get("assignment")  # ✅ For submissions tab

    now = timezone.now()
    assignments = Assignment.objects.filter(course__in=courses)

    # Filter by course
    if selected_course:
        assignments = assignments.filter(course_id=selected_course)

    # Filter by search
    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    active_assignments = assignments.filter(due_date__gte=now)
    completed_assignments = assignments.filter(due_date__lt=now)

    # Submission tracking logic
    submitted_students = not_submitted_students = submissions = None
    selected_assignment = None

    if selected_assignment_id:
        try:
            selected_assignment = Assignment.objects.get(id=selected_assignment_id, course__in=courses)
            students = CustomUser.objects.filter(role='student', assigned_teacher=user)
            submissions = Submission.objects.filter(assignment=selected_assignment)
            submitted_ids = submissions.values_list("student_id", flat=True)
            submitted_students = students.filter(id__in=submitted_ids)
            not_submitted_students = students.exclude(id__in=submitted_ids)
        except Assignment.DoesNotExist:
            selected_assignment = None

    # Handle POSTs (create/edit/delete)
    if request.method == "POST":
        if "create_assignment" in request.POST:
            form = AssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment = form.save(commit=False)
                if assignment.course.instructor != teacher:
                    return redirect("teacher_assignments")
                assignment.status = "draft" if request.POST.get("is_draft") == "on" else "active"
                assignment.save()
                return redirect("teacher_assignments")
            else:
                create_form = form
                edit_forms = {}
        elif "edit_assignment_id" in request.POST:
            assignment_id = request.POST.get("edit_assignment_id")
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            if assignment.course.instructor != teacher:
                return redirect("teacher_assignments")

            form = AssignmentForm(request.POST, request.FILES, instance=assignment)
            if form.is_valid():
                updated = form.save(commit=False)
                updated.status = "draft" if request.POST.get("is_draft") == "on" else "active"
                if not request.FILES.get("attachment"):
                    updated.attachment = assignment.attachment
                updated.save()
                return redirect("teacher_assignments")
            else:
                create_form = AssignmentForm()
                edit_forms = {assignment.id: form}
        elif "delete_assignment_id" in request.POST:
            assignment_id = request.POST.get("delete_assignment_id")
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            if assignment.course.instructor != teacher:
                return redirect("teacher_assignments")
            assignment.delete()
            return redirect("teacher_assignments")
    else:
        create_form = AssignmentForm()
        edit_forms = {}
    
    context = {
        "courses": courses,
        "selected_course": selected_course,
        "search_query": search_query,
        "selected_assignment_id": selected_assignment_id,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
        "create_form": create_form,
        "edit_forms": edit_forms,
        "selected_assignment": selected_assignment,
        "submitted_students": submitted_students,
        "not_submitted_students": not_submitted_students,
        "submissions": submissions,
    }
    return render(request, "core/teacher/teacher_assignments.html", context)

@login_required
def assignment_create(request):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    if not teacher:
        return redirect("index")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            if assignment.course.instructor != teacher:
                return redirect("teacher_assignments")
            assignment.save()
            return redirect("teacher_assignments")
        else:
            # Return form errors on the same page (you must update your template to show these)
            courses = Course.objects.filter(instructor=teacher)
            context = {"form": form, "courses": courses}
            return render(request, "core/teacher/teacher_assignments.html", context)
    return redirect("teacher_assignments")

@login_required
def assignment_edit(request, pk):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.course.instructor != teacher:
        return redirect("teacher_assignments")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
        return redirect("teacher_assignments")
    return redirect("teacher_assignments")


@login_required
def assignment_delete(request, pk):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    assignment = get_object_or_404(Assignment, pk=pk)
    if assignment.course.instructor != teacher:
        return redirect("teacher_assignments")

    if request.method == "POST":
        assignment.delete()
    return redirect("teacher_assignments")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.timezone import now
from .models import Discussion, Course
from .forms import DiscussionForm


@login_required
def teacher_discussions(request):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    if not teacher:
        return redirect("index")

    courses = Course.objects.filter(instructor=teacher)

    # Filters from GET
    filter_course = request.GET.get("course", "all")
    filter_status = request.GET.get("status", "all")
    search_query = request.GET.get("q", "").strip()

    discussions = Discussion.objects.all()

    # Filter by course
    if filter_course != "all":
        if filter_course == "none":
            discussions = discussions.filter(course__isnull=True)
        else:
            discussions = discussions.filter(course_id=filter_course)

    # Filter by status
    if filter_status != "all":
        discussions = discussions.filter(status=filter_status)

    # Search filter (title/content)
    if search_query:
        discussions = discussions.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    # Order pinned discussions first, then recent
    discussions = discussions.order_by("-pinned", "-created_at")

    # Pagination
    paginator = Paginator(discussions, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Stats
    active_discussions_count = Discussion.objects.filter(status="active").count()
    total_replies = DiscussionReply.objects.count()

    # Response rate: % of discussions with at least one reply
    total_discussions = Discussion.objects.count()
    discussions_with_replies = (
        Discussion.objects.annotate(reply_count=Count("replies"))
        .filter(reply_count__gt=0)
        .count()
    )
    response_rate = (
        round((discussions_with_replies / total_discussions * 100), 2)
        if total_discussions
        else 0
    )

    context = {
        "courses": courses,
        "discussions": page_obj,
        "filter_course": filter_course,
        "filter_status": filter_status,
        "search_query": search_query,
        "active_discussions_count": active_discussions_count,
        "total_replies": total_replies,
        "response_rate": response_rate,
    }
    return render(request, "core/teacher/teacher_discussion.html", context)


@login_required
def create_discussion(request):
    user = request.user
    teacher = getattr(user, "teacher_profile", None)
    if not teacher:
        return redirect("index")

    if request.method == "POST":
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.creator = user
            # Treat 'none' course value as None (General)
            if discussion.course and discussion.course == "none":
                discussion.course = None
            discussion.save()
            return redirect("teacher_discussions")
    else:
        form = DiscussionForm()

    return render(request, "core/teacher/teacher_discussion.html", {"form": form})


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import LibraryContent, Course
from .forms import LibraryContentUploadForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LibraryContent, Course
from .forms import LibraryContentUploadForm
from django.core.paginator import Paginator


@login_required
def teacher_library(request):
    teacher = request.user.teacher_profile  # Assumes teacher relation exists

    # Filter
    course_id = request.GET.get("course")
    search_query = request.GET.get("search")
    contents = LibraryContent.objects.filter(uploaded_by=request.user)

    if course_id:
        contents = contents.filter(course__id=course_id)
    if search_query:
        contents = contents.filter(title__icontains=search_query)

    # Upload form POST
    if request.method == "POST":
        form = LibraryContentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.uploaded_by = request.user
            content.save()
            return redirect("teacher_library")  # Or your URL name
    else:
        form = LibraryContentUploadForm()

    paginator = Paginator(contents.order_by("-uploaded_at"), 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "contents": page_obj,
        "courses": Course.objects.filter(instructor=teacher),
        "form": form,
        "page_obj": page_obj,
    }
    return render(request, "core/teacher/teacher_library.html", context)


from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
import json
import pandas as pd

from .models import CustomUser, Course
from .forms import AddStudentForm, UploadExcelForm

@login_required
def teacher_students(request):
    teacher = request.user.teacher_profile  # Assumes CustomUser → Teacher OneToOne
    temp_password = "Student@123"

    add_form = AddStudentForm()
    upload_form = UploadExcelForm()

    # --- Handle Excel Upload ---
    if request.method == "POST" and "upload_excel" in request.POST:
        upload_form = UploadExcelForm(request.POST, request.FILES)
        if upload_form.is_valid():
            excel_file = upload_form.cleaned_data["file"]
            try:
                df = pd.read_excel(excel_file, engine="openpyxl")
                required_cols = ["S.No", "Student Name", "Roll Number", "Phone Number", "Email Address"]
                if not all(col in df.columns for col in required_cols):
                    messages.error(request, "Excel file must contain columns: S.No, Student Name, Roll Number, Phone Number, Email Address")
                else:
                    
                    added_count = 0
                    for _, row in df.iterrows():
                        with transaction.atomic():
                            roll_number = str(row["Roll Number"]).strip()
                            email = str(row["Email Address"]).strip()
                            full_name = str(row["Student Name"]).strip()
                            phone = str(row["Phone Number"]).strip()
                            if not roll_number or not email or not full_name:
                                continue  # skip empty or malformed rows
                            # Avoid duplicate email or roll number
                            if CustomUser.objects.filter(email=email).exists():
                                continue
                            if Student.objects.filter(roll_number=roll_number).exists():
                                continue
                            first_name = full_name.split()[0]
                            last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
                            user = CustomUser.objects.create_user(
                                email=email,
                                password=temp_password,
                                first_name=first_name,
                                last_name=last_name,
                                role="student",
                            )
                            student_profile = user.student_profile
                            student_profile.assigned_teacher = teacher
                            student_profile.roll_number = roll_number
                            student_profile.phone = phone
                            student_profile.save()
                            added_count += 1

                    messages.success(request, f"{added_count} students uploaded successfully.")
            except Exception as e:
                messages.error(request, f"Error processing Excel file: {str(e)}")

            return redirect("teacher_students")

    # --- Handle Manual Add ---
    if request.method == "POST" and "add_student" in request.POST:
        add_form = AddStudentForm(request.POST)
        if add_form.is_valid():
            full_name = add_form.cleaned_data["full_name"].strip()
            email = add_form.cleaned_data["email"].strip()
            courses = add_form.cleaned_data["courses"]
            notes = add_form.cleaned_data["notes"]

            first_name = full_name.split()[0]
            last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""

            user = CustomUser.objects.create_user(
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                role="student",
            )
            student_profile = user.student_profile
            student_profile.assigned_teacher = teacher
            student_profile.notes = notes
            student_profile.save()
            if courses:
                student_profile.courses.set(courses)
            messages.success(request, "Student added successfully.")
            return redirect("teacher_students")

    # --- Filters & Query ---
    students = CustomUser.objects.filter(role="student", student_profile__assigned_teacher=teacher)

    course_filter = request.GET.get("course_filter")
    status_filter = request.GET.get("status_filter")
    search_query = request.GET.get("search")

    if course_filter:
        students = students.filter(student_profile__courses__id=course_filter)

    if status_filter == "active":
        students = students.filter(is_active=True)
    elif status_filter == "inactive":
        students = students.filter(is_active=False)

    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        ).distinct()

    paginator = Paginator(students.order_by("first_name", "last_name"), 12)
    page_number = request.GET.get("page")
    students_page = paginator.get_page(page_number)

    # --- Chart Data ---
    active_count = students.filter(is_active=True).count()
    inactive_count = students.filter(is_active=False).count()
    activity_labels = ['Active', 'Inactive']
    activity_counts = [active_count, inactive_count]

    context = {
        "students": students_page,
        "course_categories": Course.objects.filter(instructor=teacher).values("id", "title").distinct(),
        "add_form": add_form,
        "upload_form": upload_form,
        "temp_password": temp_password,
        "activity_labels": mark_safe(json.dumps(activity_labels)),
        "activity_counts": mark_safe(json.dumps(activity_counts)),
    }

    return render(request, "core/teacher/teacher_student.html", context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, Submission, Student, CustomUser

