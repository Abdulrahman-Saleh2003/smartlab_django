# patient_test_history/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class PatientTestHistory(models.Model):
    history_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف السجل التاريخي"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='test_history',
        verbose_name="المريض"
    )

    test = models.ForeignKey(
        'lab_tests.LabTest',
        on_delete=models.PROTECT,
        related_name='patient_history',
        verbose_name="نوع التحليل"
    )

    result = models.ForeignKey(
        'test_results.TestResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_entries',
        verbose_name="النتيجة المرتبطة (اختياري)"
    )

    value = models.FloatField(
        _("القيمة المسجلة"),
        help_text="القيمة الفعلية في هذا التاريخ"
    )

    unit = models.CharField(
        _("الوحدة"),
        max_length=50,
        blank=True
    )

    recorded_at = models.DateTimeField(
        _("تاريخ التسجيل"),
        default=timezone.now
    )

    status = models.CharField(
        _("حالة النتيجة"),
        max_length=20,
        choices=[
            ('normal', 'طبيعي'),
            ('low', 'منخفض'),
            ('high', 'مرتفع'),
            ('abnormal', 'غير طبيعي'),
            ('critical', 'حرج'),
        ],
        default='normal'
    )

    notes = models.TextField(
        _("ملاحظات إضافية"),
        blank=True
    )

    class Meta:
        verbose_name = _("سجل تاريخي لتحليل")
        verbose_name_plural = _("سجلات تاريخ التحاليل")
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['patient', 'test', 'recorded_at']),
        ]

    def __str__(self):
        return f"سجل {self.history_id} - {self.test.test_name} = {self.value} ({self.recorded_at.date()})"

    @property
    def is_out_of_range(self):
        if self.test.normal_range_min is None or self.test.normal_range_max is None:
            return None
        return not (self.test.normal_range_min <= self.value <= self.test.normal_range_max)