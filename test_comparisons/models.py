# test_comparisons/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TestComparison(models.Model):
    TREND_CHOICES = (
        ('improved', 'تحسن'),
        ('worsened', 'تدهور'),
        ('stable', 'مستقر'),
        ('significant_change', 'تغيير كبير'),
        ('new_baseline', 'قاعدة جديدة'),
    )

    comparison_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المقارنة"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='test_comparisons',
        verbose_name="المريض"
    )

    test = models.ForeignKey(
        'lab_tests.LabTest',
        on_delete=models.PROTECT,
        related_name='comparisons',
        verbose_name="نوع التحليل"
    )

    old_result = models.ForeignKey(
        'test_results.TestResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='old_comparisons',
        verbose_name="النتيجة القديمة"
    )

    new_result = models.ForeignKey(
        'test_results.TestResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_comparisons',
        verbose_name="النتيجة الجديدة"
    )

    trend = models.CharField(
        _("الاتجاه / النتيجة"),
        max_length=30,
        choices=TREND_CHOICES,
        default='stable'
    )

    change_percentage = models.FloatField(
        _("نسبة التغيير (%)"),
        null=True,
        blank=True,
        help_text="نسبة التغيير بين القديم والجديد (موجب أو سالب)"
    )

    created_at = models.DateTimeField(
        _("تاريخ المقارنة"),
        default=timezone.now
    )

    class Meta:
        verbose_name = _("مقارنة تحليل")
        verbose_name_plural = _("مقارنات التحاليل")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'test', 'created_at']),
        ]
        unique_together = ['patient', 'test', 'new_result']  # ما نعمل مقارنة مكررة لنفس النتيجة

    def __str__(self):
        return f"مقارنة {self.comparison_id} - {self.test.test_name} ({self.trend})"

    def calculate_change(self):
        """حساب نسبة التغيير تلقائيًا إذا كانت النتيجتان موجودتان"""
        if self.old_result and self.new_result and self.old_result.value != 0:
            change = ((self.new_result.value - self.old_result.value) / self.old_result.value) * 100
            self.change_percentage = round(change, 2)
            self.save(update_fields=['change_percentage'])