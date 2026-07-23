# patients/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Patient


@receiver(post_save, sender=CustomUser)
def create_patient_profile(sender, instance, created, **kwargs):
    
    def create_patient_profile(sender, instance, created, **kwargs):
    # تجاهل إنشاء تلقائي إذا كان التسجيل من patient_register
     if created and instance.role == 'patient' and not hasattr(instance, '_from_patient_register'):
        Patient.objects.create(user=instance)
    # if created and instance.role == 'patient':
    #     Patient.objects.create(user=instance)