
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

    PRIORITY_CHOICES = (
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('urgent', 'مستعجل'),
    )


    CATEGORY_CHOICES = (
        ('laboratory', 'تحاليل مخبرية'),
        ('radiology', 'تحاليل شعاعية / تصوير طبي'),
        ('pathology', 'تحاليل نسجية (خزعات)'),
        ('functional', 'تحاليل وظيفية (تخطيط)'),
        ('genetic', 'تحاليل جينية'),
        ('nuclear', 'تحاليل نووية'),
        ('endoscopy', 'تنظير'),
        ('other', 'أخرى'),
    )


    REPORT_TYPE_CHOICES = (
        ('blood', 'تحليل دم'),
        ('urine', 'تحليل بول'),
        ('hormones', 'تحليل هرمونات'),
        ('biochemistry', 'كيمياء حيوية'),
        ('microbiology', 'أحياء دقيقة / زراعة'),
        ('xray', 'أشعة سينية (X-Ray)'),
        ('ct', 'تصوير طبقي محوري (CT)'),
        ('mri', 'رنين مغناطيسي (MRI)'),
        ('ultrasound', 'سونار / موجات فوق صوتية'),
        ('ecg', 'تخطيط قلب'),
        ('eeg', 'تخطيط دماغ'),
        ('biopsy', 'خزعة نسيجية'),
        ('dna', 'فحص حمض نووي'),
        ('other', 'أخرى'),
    )

    
    BODY_PART_CHOICES = (
        ('head', 'الرأس / الدماغ'),
        ('neck', 'الرقبة'),
        ('chest', 'الصدر'),
        ('heart', 'القلب'),
        ('abdomen', 'البطن'),
        ('pelvis', 'الحوض'),
        ('spine', 'العمود الفقري / الظهر'),
        ('upper_limbs', 'الأطراف العلوية (يد/كتف)'),
        ('lower_limbs', 'الأطراف السفلية (رجل/ركبة)'),
        ('teeth', 'الأسنان'),
        ('eyes', 'العيون'),
        ('full_body', 'كامل الجسم'),
        ('other', 'غير ذلك / غير محدد'),
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

 

    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_lab_reports',
        verbose_name="من رفع التقرير"
    )


    body_part = models.CharField(
        _("الجزء المستهدف من الجسم"),
        max_length=20,
        choices= BODY_PART_CHOICES,
        null=True,   
        blank=True,   
        help_text= "The Part of the body that was examined (leave blank for laboratory tests)"

    )
   

    category = models.CharField(
        _("نوع التحليل"),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='laboratory'
    )
     
     
    report_type = models.CharField(
        _("نوع التقرير"),
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        default='blood'
    )

    
    title = models.CharField(
        _("عنوان التقرير"),
        max_length=255,
        blank=True
    )

   
    description = models.TextField(
        _("وصف التقرير"),
        blank=True
    )


    lab_name = models.CharField(
        _("اسم المختبر / المركز"),
        max_length=255,
        help_text="اسم المختبر اللي عمل التحليل"
    )


    priority = models.CharField(
        _("الأولوية"),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )

    
    report_date = models.DateField(
        _("تاريخ التقرير"),
        help_text="تاريخ إصدار التقرير الرسمي"
    )


    upload_date = models.DateTimeField(
        _("تاريخ الرفع"),
        default=timezone.now
    )

    
    file_path = models.FileField(
        _("ملف التقرير"),
        upload_to='lab_reports/%Y/%m/%d/',
        blank=True,
        null=True
    )


    status = models.CharField(
        _("حالة التقرير"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

     
    cost = models.DecimalField(
        _("تكلفة التحليل"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    internal_notes = models.TextField(blank=True)

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
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"تقرير {self.report_id} - {self.lab_name} ({self.report_date}) لـ {self.patient.user.name}"

    @property
    def is_recent(self):
        return (timezone.now() - self.upload_date).days <= 7

     
 










 