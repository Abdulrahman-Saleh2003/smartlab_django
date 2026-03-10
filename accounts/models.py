from django.db import models

# Create your models here.
# accounts/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
        blank=True,
        null=True
    )
    
    birth_date = models.DateField(_("تاريخ الميلاد"), blank=True, null=True)
    
    phone = models.CharField(_("رقم الهاتف"), max_length=20, blank=True)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), default=timezone.now)
    
    last_login = models.DateTimeField(_("آخر تسجيل دخول"), blank=True, null=True)

    is_active = models.BooleanField(_("نشط"), default=True)
    is_staff = models.BooleanField(_("عضو في الإدارة"), default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمين")
        ordering = ['-created_at']

    def __str__(self):
        return self.email
    
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