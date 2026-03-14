# lab_technicians/models.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class LabTechnician(models.Model):
    technician_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المخبري"
    )

    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'lab_technician'},
        related_name='lab_technician_profile',
        verbose_name="المستخدم المرتبط"
    )

    lab_specialty = models.CharField(
        _("تخصص المختبر"),
        max_length=255,
        blank=True,
        help_text="مثال: تحاليل دم، أشعة، باثولوجي..."
    )

    license_number = models.CharField(
        _("رقم ترخيص المختبر"),
        max_length=100,
        blank=True,
        unique=True,
        help_text="رقم الترخيص المهني للمخبري (اختياري)"
    )


    lab_location = models.CharField(
            _("موقع المختبر"),
            max_length=255,
            blank=True,
            null=True,
            help_text="اسم المختبر أو العنوان (مثال: مختبر الشام - دمشق، حي المزة)"
        )
    years_of_experience = models.PositiveIntegerField(
        _("سنوات الخبرة"),
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("مخبري")
        verbose_name_plural = _("المخبريين")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.user.email}"