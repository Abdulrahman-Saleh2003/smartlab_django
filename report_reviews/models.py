
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class report_review(models.Model):

    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المراجعة"
    )


    report = models.ForeignKey(
        'lab_reports.LabReport',
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name=_("التقرير الأصلي")
    )

    
    patient = models.ForeignKey(
        'patients.Patient', 
        on_delete=models.CASCADE, 
        related_name='medical_reviews',
        verbose_name=_("المريض")
    )


    # doctor = models.ForeignKey(
    #     'accounts.CustomUser',  
    #     on_delete=models.PROTECT, 
    #     related_name='doctor_reviews',
    #     verbose_name=_("الطبيب المراجع")
    # )

    doctor = models.ForeignKey(
        'doctors.Doctor',  # ربط مباشر بجدول الطبيب (البروفايل)
        on_delete=models.PROTECT, 
        related_name='doctor_reviews',
        verbose_name=_("الطبيب المراجع")
    )


   
    clinical_finding = models.TextField(
        _("النتائج السريرية"), 
        help_text=_("What did the doctor see in the lab results or imaging? Describe any abnormalities, patterns, or significant findings.")

    )


    diagnosis = models.CharField(
        _("التشخيص المبدئي/النهائي"), 
        max_length=500, 
        blank=True
    )


    comparison_with_previous = models.TextField(
        _("مقارنة مع تقارير سابقة"), 
        blank=True,
        help_text=_("Compare the current report with previous ones. Is there improvement, deterioration, or stability? This helps in understanding the progression of the patient's condition.")

    )

    
    recommendations = models.TextField(
        _("التوصيات الطبية"), 
        help_text=_("Based on the findings, what are your recommendations for the next steps? This could include further tests, referrals to specialists, or specific treatments.")

    )


    prescribed_medication = models.TextField(
        _("الأدوية الموصوفة بناءً على التقرير"), 
        blank=True
    )


    require_urgent_action = models.BooleanField(
        _("يتطلب إجراء عاجل؟"), 
        default=False
    )

   
    REVIEW_RESULT_CHOICES = (
        ('normal', 'نتائج طبيعية'),
        ('abnormal', 'نتائج غير طبيعية - مستقرة'),
        ('critical', 'حالة حرجة'),
        ('inconclusive', 'غير حاسم - يتطلب فحوصات إضافية'),
    )


    result_interpretation = models.CharField(
        _("تفسير الحالة"), 
        max_length=20, 
        choices=REVIEW_RESULT_CHOICES, 
        default='normal'
    )
    

    doctor_notes = models.TextField(_("ملاحظات الطبيب الخاصة"), blank=True)


    review_date = models.DateTimeField(
        _("تاريخ المراجعة"), 
        auto_now_add=True
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
        verbose_name = _("مراجعة طبية")
        verbose_name_plural = _("مراجعات طبية")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor', 'patient']),   
        ]

    def __str__(self):
        return f"مراجعة {self.review_id} - د. {self.doctor.user.name} لـ {self.patient.user.name}"
    


 
