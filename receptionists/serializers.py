# receptionists/serializers.py
from rest_framework import serializers
from .models import Receptionist
from accounts.serializers import UserSerializer
from accounts.models import CustomUser
import random


class ReceptionistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Receptionist
        fields = [
            'receptionist_id',
            'user',
            'salary',
            'work_type',
            'working_hours',
            'shift_start_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['receptionist_id', 'created_at', 'updated_at']


class ReceptionistRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")
    name = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    national_id = serializers.CharField(max_length=15, required=True)

    # الحقول الإضافية للموظف (اختيارية)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    work_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    working_hours = serializers.IntegerField(required=False)
    shift_start_time = serializers.TimeField(required=False)

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

        random_code = ''.join(random.choices('0123456789', k=10))

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role='receptionist',
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            national_id=validated_data['national_id'],
            random_code=random_code,
        )

        if hasattr(user, 'receptionist_profile'):
            raise serializers.ValidationError("بروفايل موظف الاستقبال موجود مسبقًا")

        Receptionist.objects.create(
            user=user,
            salary=validated_data.get('salary'),
            work_type=validated_data.get('work_type', ''),
            working_hours=validated_data.get('working_hours'),
            shift_start_time=validated_data.get('shift_start_time'),
        )

        return user