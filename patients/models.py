# patients/models.py

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Patient(models.Model):
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('unknown', 'غير معروف'),
    )

    patient_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المريض"
    )

    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_profile',
        verbose_name="المستخدم المرتبط"
    )

    blood_type = models.CharField(
        _("فصيلة الدم"),
        # max_length=5,
        # max_length=10,
        max_length=7,
        choices=BLOOD_TYPE_CHOICES,
        default='unknown'
    )

    chronic_diseases = models.TextField(
        _("الأمراض المزمنة"),
        blank=True,
        help_text="اكتب الأمراض المزمنة مفصولة بفواصل أو سطور جديدة"
    )

    allergies = models.TextField(
        _("الحساسية"),
        blank=True,
        help_text="اكتب أنواع الحساسية (أدوية، طعام، مواد...) مفصولة بفواصل"
    )

    height = models.FloatField(
        _("الطول"),
        null=True,
        blank=True,
        help_text="بالسنتيمتر (مثال: 175.5)"
    )

    weight = models.FloatField(
        _("الوزن"),
        null=True,
        blank=True,
        help_text="بالكيلوغرام (مثال: 75.0)"
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
        verbose_name = _("مريض")
        verbose_name_plural = _("المرضى")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.user.email}"

    @property
    def bmi(self):
        """حساب مؤشر كتلة الجسم (BMI) إذا كان الطول والوزن موجودين"""
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None