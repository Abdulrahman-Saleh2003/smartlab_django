# lab_tests/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class LabTest(models.Model):
    test_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف التحليل"
    )

    test_name = models.CharField(
        _("اسم التحليل"),
        max_length=255,
        help_text="مثال: Glucose, Hemoglobin, TSH..."
    )

    loinc_code = models.CharField(
        _("كود LOINC"),
        max_length=50,
        blank=True,
        help_text="الكود الدولي من Logical Observation Identifiers Names and Codes"
    )

    category = models.CharField(
        _("الفئة"),
        max_length=100,
        blank=True,
        help_text="مثال: Hematology, Biochemistry, Endocrinology, Microbiology..."
    )

    normal_range_min = models.FloatField(
        _("الحد الأدنى الطبيعي"),
        null=True,
        blank=True
    )

    normal_range_max = models.FloatField(
        _("الحد الأعلى الطبيعي"),
        null=True,
        blank=True
    )

    unit = models.CharField(
        _("الوحدة"),
        max_length=50,
        blank=True,
        help_text="مثال: mg/dL, g/L, IU/mL, %..."
    )

    description = models.TextField(
        _("الوصف / الملاحظات"),
        blank=True,
        help_text="معلومات إضافية عن التحليل أو الطريقة"
    )

    created_at = models.DateTimeField(
        _("تاريخ الإنشاء"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("آخر تحديث"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("تحليل مخبري")
        verbose_name_plural = _("التحاليل المخبرية")
        ordering = ['test_name']
        indexes = [
            models.Index(fields=['test_name']),
            models.Index(fields=['loinc_code']),
        ]
        unique_together = ['test_name', 'loinc_code']  # لمنع التكرار

    def __str__(self):
        return f"{self.test_name} ({self.loinc_code or 'بدون كود'})"

    @property
    def normal_range_display(self):
        if self.normal_range_min is not None and self.normal_range_max is not None:
            return f"{self.normal_range_min} - {self.normal_range_max} {self.unit}"
        return "غير محدد"