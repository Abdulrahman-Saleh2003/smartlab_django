# report_sharing/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ReportSharing(models.Model):
    PERMISSION_CHOICES = (
        ('view', 'عرض فقط'),
        ('view_download', 'عرض + تحميل'),
        ('edit', 'تعديل (نادر)'),
        ('full_access', 'وصول كامل (نادر جدًا)'),
    )

    share_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المشاركة"
    )

    # report = models.ForeignKey(
    #     'reports.LabReports',
    #     on_delete=models.CASCADE,
    #     related_name='sharings',
    #     verbose_name="التقرير المشترك"
    # )

    report = models.ForeignKey(
        'lab_reports.LabReport',
        on_delete=models.CASCADE,
        related_name='shared_reports',
        verbose_name="التقرير المشترك"
    )


    shared_with = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='shared_reports',
        verbose_name="الطبيب المشترك معه"
    )

    permission = models.CharField(
        _("مستوى الصلاحية"),
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='view'
    )

    shared_at = models.DateTimeField(
        _("تاريخ المشاركة"),
        default=timezone.now
    )

    expires_at = models.DateTimeField(
        _("تاريخ انتهاء الصلاحية"),
        null=True,
        blank=True,
        help_text="اختياري: متى تنتهي صلاحية المشاركة"
    )

    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sharings',
        verbose_name="من قام بالمشاركة"
    )

    class Meta:
        verbose_name = _("مشاركة تقرير")
        verbose_name_plural = _("مشاركات التقارير")
        ordering = ['-shared_at']
        unique_together = ['report', 'shared_with']  # ما يقدر يشارك نفس التقرير مرتين لنفس الطبيب
        indexes = [
            models.Index(fields=['report', 'shared_with']),
        ]

    def __str__(self):
        return f"مشاركة {self.share_id} - تقرير {self.report} مع د. {self.shared_with.user.name}"

    def is_active(self):
        if self.expires_at is None:
            return True
        return timezone.now() < self.expires_at
    
    
    # report_sharing/models.py

# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone

# class ReportSharing(models.Model):
#     PERMISSION_CHOICES = (
#         ('view', 'عرض فقط'),
#         ('view_download', 'عرض + تحميل'),
#         ('edit', 'تعديل (نادر)'),
#         ('full_access', 'وصول كامل (نادر جدًا)'),
#     )

#     share_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     report = models.ForeignKey('reports.LabReports', on_delete=models.CASCADE, related_name='sharings')
#     shared_with = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='shared_reports')
#     permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
#     shared_at = models.DateTimeField(default=timezone.now)
#     expires_at = models.DateTimeField(null=True, blank=True)
#     created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='created_sharings')

#     class Meta:
#         ordering = ['-shared_at']
#         unique_together = ['report', 'shared_with']

#     def __str__(self):
#         return f"مشاركة {self.share_id} لـ {self.report}"