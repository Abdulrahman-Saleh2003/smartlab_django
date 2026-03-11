# test_results/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TestResult(models.Model):
    STATUS_CHOICES = (
        ('normal', 'طبيعي'),
        ('low', 'منخفض'),
        ('high', 'مرتفع'),
        ('abnormal', 'غير طبيعي'),
        ('critical', 'حرج'),
        ('invalid', 'غير صالح / خطأ'),
    )

    result_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف النتيجة"
    )

    report = models.ForeignKey(
        'reports.LabReports',
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name="التقرير"
    )

    test = models.ForeignKey(
        'lab_tests.LabTest',
        on_delete=models.PROTECT,  # ما نحذف تحليل إذا كان مستخدم في نتيجة
        related_name='results',
        verbose_name="نوع التحليل"
    )

    value = models.FloatField(
        _("القيمة المقاسة"),
        help_text="النتيجة الفعلية من التحليل (مثال: 120.5)"
    )

    unit = models.CharField(
        _("الوحدة"),
        max_length=50,
        blank=True,
        help_text="مثال: mg/dL, mmol/L..."
    )

    status = models.CharField(
        _("حالة النتيجة"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal'
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
        verbose_name = _("نتيجة تحليل")
        verbose_name_plural = _("نتائج التحاليل")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', 'test']),
        ]

    def __str__(self):
        return f"نتيجة {self.result_id} - {self.test.test_name} = {self.value} {self.unit}"

    @property
    def is_out_of_range(self):
        """تحقق إذا القيمة خارج النطاق الطبيعي"""
        if self.test.normal_range_min is None or self.test.normal_range_max is None:
            return None
        return not (self.test.normal_range_min <= self.value <= self.test.normal_range_max)