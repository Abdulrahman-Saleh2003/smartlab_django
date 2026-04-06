# health_alerts/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class HealthAlert(models.Model):
    ALERT_TYPE_CHOICES = (
        ('critical', 'حرج / طارئ'),
        ('warning', 'تحذير'),
        ('info', 'معلوماتي / تذكير'),
        ('follow_up', 'متابعة موعد'),
        ('abnormal_result', 'نتيجة غير طبيعية'),
    )

    alert_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التنبيه"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='health_alerts',
        verbose_name="المريض"
    )

    result = models.ForeignKey(
        'ai_analysis.AIAnalysis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='health_alerts',
        verbose_name="نتيجة التحليل المرتبطة (اختياري)"
    )

    alert_type = models.CharField(
        _("نوع التنبيه"),
        max_length=50,
        choices=ALERT_TYPE_CHOICES,
        default='info'
    )

    message = models.TextField(
        _("رسالة التنبيه"),
        help_text="نص التنبيه اللي رح يشوفه المريض (مثال: 'نتيجة التحليل تشير إلى ارتفاع في السكر، يرجى زيارة الطبيب')"
    )

    is_read = models.BooleanField(
        _("مقروء؟"),
        default=False
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
        verbose_name = _("تنبيه صحي")
        verbose_name_plural = _("تنبيهات صحية")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"تنبيه {self.alert_id} - {self.alert_type} لـ {self.patient.user.name}"