# lab_reports/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class LabReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('processing', 'جاري المعالجة'),
        ('completed', 'مكتمل'),
        ('reviewed', 'تمت المراجعة'),
        ('rejected', 'مرفوض'),
        ('archived', 'مؤرشف'),
    )

    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التقرير"
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='lab_reports',
        verbose_name="المريض"
    )

    lab_name = models.CharField(
        _("اسم المختبر / المركز"),
        max_length=255,
        help_text="اسم المختبر اللي عمل التحليل"
    )

    report_date = models.DateField(
        _("تاريخ التقرير"),
        help_text="تاريخ إصدار التقرير الرسمي"
    )

    upload_date = models.DateTimeField(
        _("تاريخ الرفع إلى النظام"),
        default=timezone.now
    )

    file_path = models.FileField(
        _("مسار الملف / التقرير"),
        upload_to='lab_reports/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="الملف PDF أو الصورة الأصلية للتقرير"
    )

    status = models.CharField(
        _("حالة التقرير"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_lab_reports',
        verbose_name="من رفع التقرير"
    )

    created_at = models.DateTimeField(
        _("تاريخ الإنشاء في النظام"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("آخر تحديث"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("تقرير مختبر")
        verbose_name_plural = _("تقارير المختبر")
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['patient', 'report_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"تقرير {self.report_id} - {self.lab_name} ({self.report_date}) لـ {self.patient.user.name}"

    @property
    def is_recent(self):
        return (timezone.now() - self.upload_date).days <= 7