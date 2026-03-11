# doctors/serializers.py

from rest_framework import serializers
from .models import Doctor
from accounts.serializers import UserSerializer  # لو عايز نعرض بيانات المستخدم


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
            # لو بدك user يتعدل فقط من حساب المستخدم نفسه، خليه read_only
            # 'user',
        ]

    # اختياري: validation مخصص (مثلاً التخصص ما يكون فاضي)
    def validate_specialization(self, value):
        if not value.strip():
            raise serializers.ValidationError("التخصص مطلوب ولا يمكن أن يكون فارغًا.")
        return value.strip()

    # اختياري: لو بدك تضيف حقل محسوب (مثل اسم الطبيب الكامل)
    # def get_full_name(self, obj):
    #     return obj.user.name
    #
    # extra_kwargs أو extra fields لو بدك تضيف حقل غير موجود في الموديل
    # full_name = serializers.SerializerMethodField()

    # لو بدك تسمح بتحديث بعض الحقول فقط عند الـ update
    def update(self, instance, validated_data):
        # مثال: منع تعديل license_number بعد الإنشاء
        if 'license_number' in validated_data:
            validated_data.pop('license_number')  # أو ارمي خطأ
        return super().update(instance, validated_data)