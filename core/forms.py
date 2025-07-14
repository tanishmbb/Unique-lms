from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import (
    Teacher, CustomUser, Course, ScheduleEvent, LibraryContent,
    NotificationSettings, PushNotificationSettings, TeachingPreferences,
    Discussion
)

CustomUser = get_user_model()


# --- Authentication & Registration ---

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True,
            'autofocus': True,
        }),
        label='Email Address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True,
        }),
        label='Password'
    )


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'required': True,
        }),
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'required': True,
        }),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': True,
        }),
        required=True
    )
    role = forms.ChoiceField(
        choices=[(role, label) for role, label in CustomUser.Role.choices if role != 'student'],  # Only teacher & manager
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label="Select Role"
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I agree to Terms and Privacy Policy"
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user



# --- Teacher Profile Form ---

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'full_name', 'title', 'department', 'biography', 'interests',
            'office_location', 'office_hours', 'phone_number',
            'linkedin', 'twitter', 'website'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Comma separated interests'}),
            'office_location': forms.TextInput(attrs={'class': 'form-control'}),
            'office_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }


# --- Account Form ---

class AccountForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']  # Add more if your CustomUser model has them


# --- Notification Settings Form ---

class NotificationForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            'assignment_submissions', 'student_questions',
            'system_announcements', 'upcoming_reminders', 'weekly_digest'
        ]


# --- Push Notification Settings Form ---

class PushNotificationForm(forms.ModelForm):
    class Meta:
        model = PushNotificationSettings
        fields = [
            'assignment_submissions', 'student_questions',
            'system_announcements', 'upcoming_reminders', 'notification_sound'
        ]


# --- Teaching Preferences Form ---

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = TeachingPreferences
        fields = [
            'accept_late_submissions', 'enable_animations', 'allow_student_messaging',
            'default_course_view', 'grading_scheme', 'public_profile', 'display_density'
        ]


# --- Teacher Password Change Form ---

class TeacherSecurityForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_password")
        if new_pass and confirm_pass and new_pass != confirm_pass:
            raise forms.ValidationError("New password and confirm password do not match.")
        return cleaned_data


# --- Student Add Form ---

from django import forms
from django.contrib.auth import get_user_model
from .models import Course

User = get_user_model()

class AddStudentForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full Name")
    email = forms.EmailField(label="Email")
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),  # Dynamically set in __init__
        widget=forms.SelectMultiple,
        required=False,
        label="Courses"
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If teacher is needed, pass teacher=request.user.teacher_profile from view
        self.fields['courses'].queryset = Course.objects.all()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UploadExcelForm(forms.Form):
    file = forms.FileField(label="Excel File")

# --- Schedule Event Form ---

class ScheduleEventForm(forms.ModelForm):
    class Meta:
        model = ScheduleEvent
        exclude = ['instructor', 'created_at']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


# --- Library Content Form ---

class LibraryContentForm(forms.ModelForm):
    class Meta:
        model = LibraryContent
        fields = ['title', 'file', 'course', 'is_visible_to_students']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size should be under 10 MB.")
        return file


# --- Discussion Post Form ---
from django import forms
from .models import Discussion

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'course', 'content', 'pinned']
from django import forms
from .models import Discussion

class DiscussionPostForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'course', 'content']

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter title'}),
            'course': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Discussion details'}),
        }

from django import forms
from .models import Assignment

from django import forms

from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    is_draft = forms.BooleanField(required=False, label="Save as draft (won't be visible to students)")

    class Meta:
        model = Assignment
        fields = ['title', 'course', 'description', 'due_date', 'max_points', 'attachment']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize 'is_draft' from status field if editing
        if self.instance and self.instance.pk:
            self.fields['is_draft'].initial = (self.instance.status == 'draft')

from django import forms
from .models import LibraryContent

class LibraryContentUploadForm(forms.ModelForm):
    class Meta:
        model = LibraryContent
        fields = ['title', 'file', 'course', 'is_visible_to_students']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'is_visible_to_students': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }