# lab_technicians/serializers.py
from rest_framework import serializers
from .models import LabTechnician
from accounts.serializers import UserSerializer
from accounts.models import CustomUser
import random


from rest_framework import serializers
from patients.models import Patient
from lab_reports.models import LabReport
# from patients.serializers import PatientSerializer



class LabTechnicianSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = LabTechnician
        fields = [
            'technician_id',
            'user',
            'lab_specialty',
            'license_number',
            'years_of_experience',
            'lab_location',  
            'created_at',
            
            'updated_at',
        ]
        read_only_fields = ['technician_id', 'created_at', 'updated_at']




# ----------------------------------------------------------------------------------------

 





# class PatientOverviewSerializer(serializers.ModelSerializer):
#     user = serializers.SerializerMethodField()
#     reports_count = serializers.SerializerMethodField()
#     last_report_date = serializers.SerializerMethodField()

#     class Meta:
#         model = Patient
#         fields = [
#             'patient_id',
#             'user',
#             'blood_type',
#             'height',
#             'weight',
#             'bmi',
#             'reports_count',
#             'last_report_date',
#         ]

#     def get_user(self, obj):
#         return {
#             "name": obj.user.name,
#             "email": obj.user.email,
#             "phone": obj.user.phone,
#         }

#     def get_reports_count(self, obj):
#         return obj.lab_reports.count()

#     def get_last_report_date(self, obj):
#         last = obj.lab_reports.order_by('-report_date').first()
#         return last.report_date if last else None


 
  
            
             
            
       
           

# ----------------------------------------------------------------------------------------



class LabTechnicianRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")
    name = serializers.CharField(max_length=255)
    lab_location = serializers.CharField(max_length=255, required=False, allow_blank=True)  # ← أضف هنا
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    national_id = serializers.CharField(max_length=15, required=True)

    # حقول خاصة بالمخبري (اختيارية)
    lab_specialty = serializers.CharField(max_length=255, required=False, allow_blank=True)
    license_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False)

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

        random_code = ''.join(random.choices('0123456789', k=10))

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role='lab_technician',
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            
            national_id=validated_data['national_id'],
            random_code=random_code,
        )

        if hasattr(user, 'lab_technician_profile'):
            raise serializers.ValidationError("بروفايل المخبري موجود مسبقًا")

        LabTechnician.objects.create(
            user=user,
            lab_specialty=validated_data.get('lab_specialty', ''),
            license_number=validated_data.get('license_number', ''),
            lab_location=validated_data.get('lab_location', ''),   
            years_of_experience=validated_data.get('years_of_experience'),
        )

        return user
    


























