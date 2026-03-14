# receptionists/models.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Receptionist(models.Model):
    receptionist_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف موظف الاستقبال"
    )

    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'receptionist'},
        related_name='receptionist_profile',
        verbose_name="المستخدم المرتبط"
    )

    salary = models.DecimalField(
        _("الراتب"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="الراتب الشهري (اختياري)"
    )

    work_type = models.CharField(
        _("نوع العمل"),
        max_length=100,
        blank=True,
        null=True,
        help_text="مثال: دوام كامل، دوام جزئي، نوبات (اختياري)"
    )

    working_hours = models.PositiveIntegerField(
        _("عدد ساعات العمل"),
        null=True,
        blank=True,
        help_text="عدد الساعات الأسبوعية أو اليومية (اختياري)"
    )

    shift_start_time = models.TimeField(
        _("بداية الدوام"),
        null=True,
        blank=True,
        help_text="وقت بداية الدوام اليومي (اختياري)"
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
        verbose_name = _("موظف استقبال")
        verbose_name_plural = _("موظفي الاستقبال")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.user.email}"