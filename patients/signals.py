# patients/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Patient


@receiver(post_save, sender=CustomUser)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'patient':
        Patient.objects.create(user=instance)