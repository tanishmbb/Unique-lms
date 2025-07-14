from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager

# -------------------------------
# Custom User and Manager
# -------------------------------

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('role', CustomUser.Role.TEACHER)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        MANAGER = 'manager', 'Manager'

    username = None
    email = models.EmailField('email address', unique=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    assigned_teacher = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'teacher'},
        related_name='assigned_students'
    )

    is_deactivated = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


# -------------------------------
# Role Profiles
# -------------------------------

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    assigned_teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, blank=True, null=True, related_name='students')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=150)
    title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    website = models.URLField(blank=True)
    is_deactivated = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Manager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='manager_profile')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    office = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.email


# -------------------------------
# Courses
# -------------------------------

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    instructor = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------------------
# Modules and Assignments
# -------------------------------

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    max_points = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"


# -------------------------------
# Schedule & Live Classes
# -------------------------------

class ScheduleEvent(models.Model):
    EVENT_TYPES = [
        ('live_class', 'Live Class'),
        ('office_hours', 'Office Hours'),
        ('meeting', 'Meeting'),
        ('deadline', 'Deadline'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    instructor = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedule_events')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    repeat_weekly = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"


class LiveClass(models.Model):
    PLATFORM_CHOICES = [
        ('Zoom', 'Zoom'),
        ('Google Meet', 'Google Meet'),
        ('Microsoft Teams', 'Microsoft Teams'),
        ('Other', 'Other'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='live_classes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    meeting_link = models.URLField(blank=True, null=True)
    is_recorded = models.BooleanField(default=False)
    repeat_weekly = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.course.title}"


# -------------------------------
# Discussions and Library
# -------------------------------

class Discussion(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    pinned = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)

    def reply_count(self):
        return self.replies.count()

    def __str__(self):
        return self.title


class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussion_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LibraryContent(models.Model):
    FILE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='library_contents/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='document')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='contents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_visible_to_students = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# -------------------------------
# Notification & Teaching Settings
# -------------------------------

class NotificationSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_settings')
    assignment_submissions = models.BooleanField(default=True)
    student_questions = models.BooleanField(default=True)
    system_announcements = models.BooleanField(default=True)
    upcoming_reminders = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Settings for {self.user.email}"


class PushNotificationSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_notification_settings')
    assignment_submissions = models.BooleanField(default=True)
    student_questions = models.BooleanField(default=True)
    system_announcements = models.BooleanField(default=True)
    upcoming_reminders = models.BooleanField(default=True)
    notification_sound = models.CharField(max_length=50, default="default")

    def __str__(self):
        return f"Push Notification Settings for {self.user.email}"


class TeachingPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teaching_preferences')
    accept_late_submissions = models.BooleanField(default=True)
    enable_animations = models.BooleanField(default=True)
    allow_student_messaging = models.BooleanField(default=True)
    default_course_view = models.CharField(max_length=20, default="List")
    grading_scheme = models.CharField(max_length=50, default="Percentage")
    public_profile = models.BooleanField(default=False)
    display_density = models.CharField(max_length=20, default="Comfortable")
    default_grade_scale = models.CharField(max_length=50, default="Percentage")
    preferred_language = models.CharField(max_length=50, default="English")
    default_course_visibility = models.CharField(max_length=20, default="Private")

    def __str__(self):
        return f"Teaching Preferences for {self.user.email}"
