# patients/serializers.py

from rest_framework import serializers
from .models import Patient
from accounts.serializers import UserSerializer


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # عرض بيانات المستخدم (الاسم، الإيميل...)

    bmi = serializers.ReadOnlyField()  # خاصية محسوبة (مؤشر كتلة الجسم)

    class Meta:
        model = Patient
        fields = [
            'patient_id',
            'user',
            'blood_type',
            'chronic_diseases',
            'allergies',
            'height',
            'bmi',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'patient_id',
            'created_at',
            'updated_at',
            'bmi',
        ]

    def validate_height(self, value):
        if value is not None and (value <= 0 or value > 300):
            raise serializers.ValidationError("الطول يجب أن يكون بين 0 و 300 سم")
        return value

    def validate_weight(self, value):
        if value is not None and (value <= 0 or value > 500):
            raise serializers.ValidationError("الوزن يجب أن يكون بين 0 و 500 كجم")
        return value