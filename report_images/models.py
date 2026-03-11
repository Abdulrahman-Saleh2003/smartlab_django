# report_images/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ReportImage(models.Model):
    image_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف الصورة"
    )

    report = models.ForeignKey(
        'lab_reports.LabReport',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="التقرير المرتبط"
    )

    image_path = models.ImageField(
        _("مسار الصورة"),
        upload_to='report_images/%Y/%m/%d/',
        help_text="صورة التقرير، التحليل، الأشعة أو الوثيقة"
    )

    ocr_confidence = models.FloatField(
        _("درجة ثقة الـ OCR"),
        null=True,
        blank=True,
        help_text="من 0.0 إلى 1.0 إذا تم استخراج نص تلقائيًا"
    )

    ocr_text = models.TextField(
        _("النص المستخرج بالـ OCR"),
        blank=True,
        null=True,
        help_text="النص اللي تم استخراجه من الصورة (إذا نجح OCR)"
    )

    uploaded_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_report_images',
        verbose_name="من رفع الصورة"
    )

    uploaded_at = models.DateTimeField(
        _("تاريخ الرفع"),
        default=timezone.now
    )

    class Meta:
        verbose_name = _("صورة تقرير")
        verbose_name_plural = _("صور التقارير")
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['report', 'uploaded_at']),
        ]

    def __str__(self):
        return f"صورة {self.image_id} لتقرير {self.report.report_id}"

    @property
    def ocr_success(self):
        if self.ocr_confidence is None:
            return False
        return self.ocr_confidence >= 0.8  # يمكن تغيير الحد حسب الحاجة