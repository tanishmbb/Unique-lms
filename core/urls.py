from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
     path('', views.index, name='index'),
     path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    # teacher
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    path('courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/discussions/', views.teacher_discussions, name='teacher_discussions'),
    path('teacher/discussions/create/', views.create_discussion, name='create_discussion'),
    path('library/', views.teacher_library, name='teacher_library'),
    path('teacher/students/', views.teacher_students, name='teacher_students'),
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/assignments/create/', views.assignment_create, name='assignment_create'),
    path('teacher/assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('teacher/assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path("assignments/", views.student_assignments, name="assignments"),
    path("assignments/submit/<int:assignment_id>/", views.submit_assignment, name="submit_assignment"),
    # if detail view:
    path('student/discussions/', views.student_discussions, name='student_discussions'),



    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path("student/courses/", views.student_courses, name="student_courses"),

#      # Authentication
#     # Public   path('login/', views.CustomLoginView.as_view(), name='login'),   path('signup/', views.signup_view, name='signup'),   path('logout/', views.logout_view, name='logout'),   # Student URLs   path('student/dashboard/', views.student_dashboard, name='student_dashboard'),   path('student/courses/', views.student_courses, name='student_courses'),  # path('student/schedule/', views.student_schedule, name='student_schedule'),
#     path('student/assignments/', views.student_assignments, name='student_assignments'),
#     path('student/discussions/', views.student_discussions, name='student_discussions'),
#     # Teacher URLs
#     path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
#     path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
#     path('teacher/courses/create/', views.create_course, name='create_course'),
#     path('teacher/course/<int:course_id>/assign-student/', views.assign_student_to_course, name='assign_student_to_course'),
#     # Assignments (teacher)
#     path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
#     path('teacher/assignments/create/', views.create_assignment, name='assignment_create'),
#     path('teacher/assignments/<int:assignment_id>/edit/', views.assignment_edit, name='assignment_edit'),
#     path('teacher/assignments/<int:assignment_id>/get/', views.get_assignment, name='assignment_get'),
#     path('teacher/assignments/<int:assignment_id>/update/', views.update_assignment, name='assignment_update'),
#     path('teacher/assignments/<int:assignment_id>/delete/', views.delete_assignment, name='assignment_delete'),
#     path('teacher/assignments/<int:assignment_id>/submissions/', views.get_submissions, name='assignment_submissions'),
#     # Students management (teacher)
#     path('teacher/students/', views.teacher_students, name='teacher_students'),
#     path('teacher/student/<int:student_id>/activate/', views.activate_student, name='activate_student'),
#     path('teacher/student/<int:student_id>/deactivate/', views.deactivate_student, name='deactivate_student'),   path('teacher/student/<int:student_id>/profile/', views.view_student_profile, name='view_student_profile'),
#      path('teacher/student/<int:student_id>/message/', views.message_student, name='message_student'),
#      path('teacher/student/<int:student_id>/progress/', views.student_progress, name='student_progress'),
#      # Teacher Discussions
#      path('teacher/discussion/', views.teacher_discussions, name='teacher_discussion'),
#      path('teacher/discussion/create/', views.create_discussion, name='create_discussion'),
#      # Teacher Schedule
#      path('teacher/schedule/', views.teacher_schedule_view, name='teacher_schedule'),
#      path('teacher/schedule/add/', views.add_schedule_event, name='add_schedule_event'),
#      path('teacher/schedule/edit/<int:event_id>/', views.edit_schedule_event, name='edit_schedule_event'),
#      path('teacher/schedule/delete/<int:event_id>/', views.delete_schedule_event, name='delete_schedule_event'),
#      path('teacher/schedule/save/', views.schedule_event_save, name='schedule_event_save'),
#   # Teacher Library
#      path('teacher/library/', views.content_library, name='content_library'),
#      # Teacher Live Classes
#      path('teacher/liveclasses/', views.teacher_liveclasses, name='teacher_liveclasses'),
#      path('teacher/liveclasses/schedule/', views.teacher_schedule_class, name='teacher_schedule_class'),
#      # Teacher Settings
#     path('teacher/settings/', views.teacher_settings, name='teacher_settings'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
