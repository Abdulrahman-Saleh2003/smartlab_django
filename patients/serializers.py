# patients/serializers.py

import random

from rest_framework import serializers
from .models import Patient
from accounts.serializers import UserSerializer
from accounts.models import CustomUser


from accounts.models import CustomUser, generate_unique_user_random_code

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # عرض بيانات المستخدم (الاسم، الإيميل...)

    bmi = serializers.ReadOnlyField()  # خاصية محسوبة (مؤشر كتلة الجسم)

    class Meta:
        model = Patient
        fields = [
            'patient_id',
            'user',
            'blood_type',
            # 'chronic_diseases',
            # 'allergies',
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
        
       
class PatientRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")
    name = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    national_id = serializers.CharField(max_length=15, required=True)  # ← إضافة جديدة

    # حقول خاصة بالمريض
    blood_type = serializers.ChoiceField(choices=Patient.BLOOD_TYPE_CHOICES, default='unknown')
    # chronic_diseases = serializers.CharField(required=False, allow_blank=True)
    # allergies = serializers.CharField(required=False, allow_blank=True)
    height = serializers.FloatField(required=False, min_value=0, max_value=300)
    weight = serializers.FloatField(required=False, min_value=0, max_value=500)

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

        return data
    


    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا الإيميل مستخدم مسبقًا")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')

         
        # random_code = ''.join(random.choices('0123456789', k=10))

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role='patient',
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            national_id=validated_data['national_id'],
            # random_code=random_code

            random_code=generate_unique_user_random_code(),
        )

        # تحقق إضافي (حماية)
        if hasattr(user, 'patient_profile'):
            raise serializers.ValidationError("بروفايل المريض موجود مسبقًا")

        # إنشاء بروفايل المريض
        Patient.objects.create(
            user=user,
            blood_type=validated_data.get('blood_type', 'unknown'),
            # chronic_diseases=validated_data.get('chronic_diseases', ''),
            # allergies=validated_data.get('allergies', ''),
            height=validated_data.get('height'),
            weight=validated_data.get('weight'),
        )

        return user
    
    
    

        
        
class PatientSearchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['patient_id', 'user']

    def get_user(self, obj):
        return {
            "name": obj.user.name,
            "random_code": obj.user.random_code,
            "national_id": obj.user.national_id,
            "phone": obj.user.phone
        }



        
 