from django.db import models

# Create your models here.
# accounts/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


import random ##################



# Update
# Helper function to generate a unique random code for users 
def generate_unique_user_random_code():
   
    # PAT-YYYY-NNNNNNN (YYYY = current year, NNNNNNN = random 7-digit number)
    from django.contrib.auth import get_user_model

    User = get_user_model()
    year = timezone.now().year
    for _ in range(200):
        suffix = "".join(random.choices("0123456789", k=7))
        code = f"PAT-{year}-{suffix}"
        if not User.objects.filter(random_code=code).exists():
            return code
    raise RuntimeError("Failed to generate a unique random code")









class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("يجب إدخال البريد الإلكتروني"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # أو أي قيمة مناسبة

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)







class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('patient', 'مريض'),
        ('doctor', 'طبيب'),
        ('admin', 'إداري'),
        ('receptionist', 'استقبال'),
        ('lab_technician', 'مخبري'),   # ← أضف هذا السطر
    )

    GENDER_CHOICES = (
        ('male', 'ذكر'),
        ('female', 'أنثى'),
        ('other', 'آخر'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="معرف المستخدم"
    )
    
    email = models.EmailField(
        _("البريد الإلكتروني"),
        unique=True,
        db_index=True,
    )
    
    
    
    name = models.CharField(_("الاسم الكامل"), max_length=255)
    
    
    national_id = models.CharField(
        _("الرقم الوطني"),
        max_length=15,
        blank=True,  # اختياري حاليًا، لو بدك إلزامي غيّر لـ blank=False
        null=True,
        unique=True,  # ← مهم: ما يتكرر
        help_text="رقم وطني مكون من 11 إلى 15 رقم"
    )

    # random_code = models.CharField(
    #     _("كود عشوائي"),
    #     max_length=10,
    #     blank=True,
    #     editable=False,  # ما يتعدل يدويًا
    #     help_text="كود 10 أرقام يُولد تلقائيًا"
    # )


    # Updatee
    ###################################################################################
    ###################################################################################
    ###################################################################################

    random_code = models.CharField(
        _("كود عشوائي"),
        max_length=24,
        blank=True,
        editable=False,  
        help_text=_("Example: PAT-2026-7891234 — Automatically generated"),
        db_index=True,
    )


    
    role = models.CharField(
        _("الدور"),
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient'
    )
    
    gender = models.CharField(
        _("الجنس"),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=False,   # ← غيّر هون إلى False (إلزامي)
        null=False     # ← غيّر هون إلى False
        # blank=True,
        # null=True
    )
    
    birth_date = models.DateField(_("تاريخ الميلاد"), blank=True, null=True)
    
    phone = models.CharField(_("رقم الهاتف"), max_length=20, 
                             
                             blank=False,   # ← غيّر هون إلى False (إلزامي)
        null=False     # ← غيّر هون إلى False
                          
                            #  blank=True
                             )
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), default=timezone.now)
    
    last_login = models.DateTimeField(_("آخر تسجيل دخول"), blank=True, null=True)

    is_active = models.BooleanField(_("نشط"), default=True)
    is_staff = models.BooleanField(_("عضو في الإدارة"), default=False)
    password_reset_code = models.CharField(max_length=6, blank=True, null=True)
    password_reset_code_expiry = models.DateTimeField(blank=True, null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']




    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمين")
        ordering = ['-created_at']


    def __str__(self):
        return self.email
    

    # Updatee
    ###################################################################################
    ###################################################################################
    ###################################################################################
    def save(self, *args, **kwargs):
        if not self.random_code:
            self.random_code = generate_unique_user_random_code()
        super().save(*args, **kwargs)











class UserActivityLog(models.Model):
    log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name="المستخدم"
    )
    
    action = models.TextField(_("الإجراء / الوصف"))
    
    created_at = models.DateTimeField(_("تاريخ الإجراء"), auto_now_add=True)

    class Meta:
        verbose_name = _("سجل نشاط")
        verbose_name_plural = _("سجلات النشاط")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action[:50]}"    