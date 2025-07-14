from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, Student, Teacher, Manager,
    CourseCategory, Course,
    Module, Assignment, Submission,
    ScheduleEvent, LiveClass, DiscussionReply,
    LibraryContent,
    NotificationSettings, PushNotificationSettings, TeachingPreferences,
)


##############################
# CustomUser Admin
##############################

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ['email']
    list_display = ('email', 'role', 'is_staff', 'is_active', 'is_deactivated')
    list_filter = ('role', 'is_staff', 'is_active', 'is_deactivated')
    search_fields = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('profile_image',)}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_deactivated', 'two_factor_enabled', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
##############################
# Student Admin
##############################
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'roll_number', 'phone_number', 'assigned_teacher')
    search_fields = ('full_name', 'roll_number', 'phone_number')
    list_filter = ('assigned_teacher',)
    raw_id_fields = ('user', 'assigned_teacher')
    ordering = ('full_name',)


##############################
# Teacher Admin
##############################
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'phone_number', 'is_deactivated')
    search_fields = ('full_name', 'department', 'phone_number')
    list_filter = ('department', 'is_deactivated')
    raw_id_fields = ('user',)
    ordering = ('full_name',)


##############################
# Manager Admin
##############################
@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'phone', 'office')
    search_fields = ('full_name', 'department', 'phone')
    raw_id_fields = ('user',)
    ordering = ('full_name',)


##############################
# CourseCategory Admin
##############################

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


##############################
# Course Admin
##############################

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'status', 'created_at')
    list_filter = ('status', 'category', 'level')
    search_fields = ('title', 'code', 'instructor__full_name')
    raw_id_fields = ('instructor',)
    ordering = ('title',)


##############################
# Enrollment Admin
##############################


##############################
# Module Admin
##############################

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')
    raw_id_fields = ('course',)
    ordering = ('course', 'order')


##############################
# Assignment Admin
##############################

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_points', 'status', 'created_at')
    list_filter = ('status', 'course')
    search_fields = ('title', 'course__title')
    raw_id_fields = ('course',)
    ordering = ('-due_date',)


##############################
# Submission Admin
##############################

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade', 'status')
    list_filter = ('status',)
    search_fields = ('assignment__title', 'student__full_name')
    raw_id_fields = ('assignment', 'student')
    ordering = ('-submitted_at',)


##############################
# ScheduleEvent Admin
##############################

@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'course', 'event_type', 'start_datetime', 'end_datetime', 'repeat_weekly')
    list_filter = ('event_type', 'repeat_weekly', 'instructor')
    search_fields = ('title', 'instructor__full_name', 'course__title')
    raw_id_fields = ('instructor', 'course')
    ordering = ('start_datetime',)


##############################
# LiveClass Admin
##############################

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'course', 'start_time', 'duration_minutes', 'platform', 'is_recorded', 'repeat_weekly')
    list_filter = ('platform', 'is_recorded', 'repeat_weekly')
    search_fields = ('title', 'teacher__full_name', 'course__title')
    raw_id_fields = ('teacher', 'course')
    ordering = ('-start_time',)


##############################
# Discussion Admin
##############################

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'creator', 'created_at')  # ✅ changed 'user' to 'creator'
    search_fields = ('discussion__title', 'creator__email', 'content')  # ✅ changed 'user__email' to 'creator__email'
    raw_id_fields = ('discussion', 'creator')  # ✅ changed 'user' to 'creator'
    ordering = ('created_at',)

##############################
# DiscussionReply Admin
##############################

class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'created_at')
    search_fields = ('discussion__title', 'user__email', 'content')
    raw_id_fields = ('discussion', 'user')
    ordering = ('created_at',)


##############################
# LibraryContent Admin
##############################

@admin.register(LibraryContent)
class LibraryContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'course', 'uploaded_by', 'uploaded_at', 'is_visible_to_students')
    list_filter = ('file_type', 'is_visible_to_students')
    search_fields = ('title', 'uploaded_by__email', 'course__title')
    raw_id_fields = ('course', 'uploaded_by')
    ordering = ('-uploaded_at',)


##############################
# Notification Settings Admin
##############################

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment_submissions', 'student_questions', 'system_announcements', 'upcoming_reminders', 'weekly_digest')
    search_fields = ('user__email',)


##############################
# Push Notification Settings Admin
##############################

@admin.register(PushNotificationSettings)
class PushNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment_submissions', 'student_questions', 'system_announcements', 'upcoming_reminders', 'notification_sound')
    search_fields = ('user__email',)


##############################
# Teaching Preferences Admin
##############################

@admin.register(TeachingPreferences)
class TeachingPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'accept_late_submissions', 'enable_animations', 'allow_student_messaging', 'default_course_view', 'grading_scheme', 'public_profile')
    search_fields = ('user__email',)
