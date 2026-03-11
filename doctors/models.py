# doctors/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Doctor(models.Model):
    doctor_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف الطبيب"
    )

    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='doctor_profile',
        verbose_name="المستخدم المرتبط"
    )

    specialization = models.CharField(
        _("التخصص"),
        max_length=255,
        help_text="مثال: جراحة عامة، طب أسنان، أمراض قلب..."
    )

    hospital = models.CharField(
        _("المستشفى / العيادة"),
        max_length=255,
        blank=True,
        help_text="اسم المستشفى أو العيادة الرئيسية"
    )

    license_number = models.CharField(
        _("رقم الترخيص المهني"),
        max_length=100,
        unique=True,
        help_text="رقم ترخيص مزاولة المهنة من النقابة أو الجهة الرسمية"
    )

    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        _("آخر تحديث"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("طبيب")
        verbose_name_plural = _("الأطباء")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.specialization}"