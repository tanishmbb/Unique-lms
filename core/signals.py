from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from .models import CustomUser, Student, Teacher, Manager

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile based on role
        if instance.role == CustomUser.Role.STUDENT:
            Student.objects.create(user=instance, full_name=instance.email)  # you can customize default full_name
        elif instance.role == CustomUser.Role.TEACHER:
            Teacher.objects.create(user=instance, full_name=instance.email)
        elif instance.role == CustomUser.Role.MANAGER:
            Manager.objects.create(user=instance, full_name=instance.email)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # Save the related profile when the user is saved
    if instance.role == CustomUser.Role.STUDENT:
        if hasattr(instance, 'student_profile'):
            instance.student_profile.save()
    elif instance.role == CustomUser.Role.TEACHER:
        if hasattr(instance, 'teacher_profile'):
            instance.teacher_profile.save()
    elif instance.role == CustomUser.Role.MANAGER:
        if hasattr(instance, 'manager_profile'):
            instance.manager_profile.save()
