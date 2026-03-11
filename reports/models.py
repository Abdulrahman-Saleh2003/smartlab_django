from django.db import models

# Create your models here.
# reports/models.py

from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class LabReports(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('rejected', 'مرفوض'),
        ('processing', 'جاري المعالجة'),
    )

    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التقرير"
    )

    patient = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='lab_reports',
        verbose_name="المريض"
    )

    lab_name = models.CharField(
        _("اسم المختبر"),
        max_length=255
    )

    report_date = models.DateField(_("تاريخ التقرير"))

    upload_date = models.DateTimeField(
        _("تاريخ الرفع"),
        default=timezone.now
    )

    file_path = models.FileField(
        _("مسار الملف"),
        upload_to='lab_reports/%Y/%m/%d/',
        blank=True,
        null=True
    )

    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("تقرير مختبر")
        verbose_name_plural = _("تقارير المختبر")
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.lab_name} - {self.patient.name} ({self.report_date})"


class ReportImages(models.Model):
    image_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف الصورة"
    )

    report = models.ForeignKey(
        LabReports,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="التقرير المرتبط"
    )

    image_path = models.ImageField(
        _("مسار الصورة"),
        upload_to='report_images/%Y/%m/%d/'
    )

    ocr_confidence = models.FloatField(
        _("درجة ثقة الـ OCR"),
        null=True,
        blank=True,
        help_text="من 0.0 إلى 1.0"
    )

    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("صورة تقرير")
        verbose_name_plural = _("صور التقارير")
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"صورة {self.image_id} - {self.report}"