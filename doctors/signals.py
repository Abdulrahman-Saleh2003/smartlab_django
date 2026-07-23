# doctors/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Doctor


@receiver(post_save, sender=CustomUser)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'doctor':
        Doctor.objects.create(user=instance)