# ai_analysis/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class AIAnalysis(models.Model):
    analysis_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التحليل"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='ai_analyses',
        verbose_name="المريض"
    )

    report = models.ForeignKey(
        'reports.LabReports',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_analyses',
        verbose_name="التقرير المرتبط (اختياري)"
    )

    prediction = models.CharField(
        _("التنبؤ / النتيجة"),
        max_length=255,
        help_text="مثال: 'التهاب رئوي'، 'طبيعي'، 'خطر متوسط'..."
    )

    confidence = models.FloatField(
        _("درجة الثقة"),
        help_text="قيمة بين 0.0 و 1.0 (مثال: 0.92 = 92% ثقة)",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        _("تاريخ التحليل"),
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        _("آخر تحديث"),
        auto_now=True
    )

    # اختياري: إذا بدك تضيف تفاصيل إضافية
    model_version = models.CharField(
        _("إصدار النموذج"),
        max_length=50,
        blank=True,
        help_text="مثال: v1.2.3 أو 'resnet50'"
    )

    class Meta:
        verbose_name = _("تحليل ذكاء اصطناعي")
        verbose_name_plural = _("تحاليل الذكاء الاصطناعي")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),  # تسريع البحث حسب المريض والتاريخ
        ]

    def __str__(self):
        return f"تحليل {self.analysis_id} - {self.prediction} ({self.confidence or 'غير محدد'})"