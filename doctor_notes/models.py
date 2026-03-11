
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class DoctorNote(models.Model):
    note_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف الملاحظة"
    )

    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='doctor_notes',
        verbose_name="الطبيب"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_notes',
        verbose_name="المريض"
    )

    report = models.ForeignKey(
        'reports.LabReports',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_notes',
        verbose_name="التقرير المرتبط (اختياري)"
    )

    note_text = models.TextField(
        _("نص الملاحظة"),
        help_text="اكتب الملاحظات الطبية، التشخيص، التوصيات، المتابعة..."
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
        verbose_name = _("ملاحظة طبيب")
        verbose_name_plural = _("ملاحظات الأطباء")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor', 'patient']),  # لتسريع البحث حسب الطبيب/المريض
        ]

    def __str__(self):
        return f"ملاحظة {self.note_id} - د. {self.doctor.user.name} لـ {self.patient.user.name}"