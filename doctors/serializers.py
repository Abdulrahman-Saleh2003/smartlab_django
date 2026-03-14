# doctors/serializers.py

import random

from rest_framework import serializers
from .models import Doctor
from accounts.serializers import UserSerializer,CustomUser  # لو عايز نعرض بيانات المستخدم


class DoctorSerializer(serializers.ModelSerializer):
    # عرض بيانات المستخدم المرتبط (الاسم، الإيميل، إلخ) بشكل مختصر أو كامل
    user = UserSerializer(read_only=True)

    # أو لو بدك تعرض بس بعض الحقول من المستخدم بدون serializer كامل
    # user_name = serializers.CharField(source='user.name', read_only=True)
    # user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'doctor_id',
            'user',
            'specialization',
            'hospital',
            'license_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'doctor_id',
            'created_at',
            'updated_at',
        ]

    # اختياري: validation مخصص (مثلاً التخصص ما يكون فاضي)
    def validate_specialization(self, value):
        if not value.strip():
            raise serializers.ValidationError("التخصص مطلوب ولا يمكن أن يكون فارغًا.")
        return value.strip()

    def update(self, instance, validated_data):
        # مثال: منع تعديل license_number بعد الإنشاء
        if 'license_number' in validated_data:
            validated_data.pop('license_number')  # أو ارمي خطأ
        return super().update(instance, validated_data)
    
class DoctorRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")  # ← أضف هذا الحقل
    name = serializers.CharField()
    specialization = serializers.CharField()
    hospital = serializers.CharField(required=False)
    license_number = serializers.CharField()
    national_id = serializers.CharField(max_length=15, required=True)
    
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    
    
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "كلمتا المرور غير متطابقتين"})


        if not data.get('gender'):
            raise serializers.ValidationError({"gender": "الجنس مطلوب"})

        phone = data.get('phone')
        if not phone:
            raise serializers.ValidationError({"phone": "رقم الهاتف مطلوب"})
        if not phone.isdigit():
            raise serializers.ValidationError({"phone": "رقم الهاتف يجب أن يكون أرقام فقط"})
        # validation الرقم الوطني
        national_id = data['national_id']
        if not national_id.isdigit():
            raise serializers.ValidationError({"national_id": "الرقم الوطني يجب أن يكون أرقام فقط"})
        if not (11 <= len(national_id) <= 15):
            raise serializers.ValidationError({"national_id": "الرقم الوطني يجب أن يكون بين 11 و15 رقم"})
        if CustomUser.objects.filter(national_id=national_id).exists():
            raise serializers.ValidationError({"national_id": "الرقم الوطني مستخدم مسبقًا"})

        # validation الترخيص
        if Doctor.objects.filter(license_number=data['license_number']).exists():
            raise serializers.ValidationError({"license_number": "رقم الترخيص مستخدم مسبقًا"})

        return data

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا الإيميل مستخدم مسبقًا")
        return value

    def validate_license_number(self, value):
      if Doctor.objects.filter(license_number=value).exists():
          raise serializers.ValidationError("رقم الترخيص مستخدم مسبقًا. يرجى استخدام رقم ترخيص آخر.")
      return value

    def create(self, validated_data):
        random_code = ''.join(random.choices('0123456789', k=10))
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role='doctor',
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            national_id=validated_data['national_id'],
            random_code=random_code,
        )
        if hasattr(user, 'doctor_profile'):
            raise serializers.ValidationError("بروفايل الطبيب موجود مسبقًا")

        Doctor.objects.create(
            user=user,
            specialization=validated_data['specialization'],
            hospital=validated_data.get('hospital', ''),
            license_number=validated_data['license_number']
        )
        return user    