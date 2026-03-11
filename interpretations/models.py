# interpretations/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Interpretation(models.Model):
    SEVERITY_CHOICES = (
        ('normal', 'طبيعي'),
        ('mild', 'خفيف'),
        ('moderate', 'متوسط'),
        ('severe', 'شديد'),
        ('critical', 'حرج / طارئ'),
    )

    interpretation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التفسير"
    )

    result = models.ForeignKey(
        'ai_analysis.AIAnalysis',
        on_delete=models.CASCADE,
        related_name='interpretations',
        verbose_name="النتيجة / التحليل المرتبط"
    )

    interpretation_text = models.TextField(
        _("نص التفسير"),
        help_text="التفسير الطبي أو التحليلي للنتيجة (مثال: 'ارتفاع في السكر يشير إلى احتمال سكري نوع 2')"
    )

    severity = models.CharField(
        _("درجة الخطورة"),
        max_length=20,
        choices=SEVERITY_CHOICES,
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

    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_interpretations',
        verbose_name="من أنشأ التفسير (AI أو طبيب)"
    )

    class Meta:
        verbose_name = _("تفسير نتيجة")
        verbose_name_plural = _("تفسيرات النتائج")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['result', 'created_at']),
        ]

    def __str__(self):
        return f"تفسير {self.interpretation_id} - {self.severity} لـ {self.result}"