
from rest_framework import serializers
from .models import CustomUser
import random
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")

    class Meta:
        model = CustomUser
        fields = [
            'email', 'name', 'password', 'password2',
            'role', 'gender', 'birth_date','phone',"national_id", 
        ]

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
        if len(phone) < 9 or len(phone) > 15:
            raise serializers.ValidationError({"phone": "رقم الهاتف يجب أن يكون بين 9 و15 رقم"})
        national_id = data.get('national_id')
        if national_id:
            if not national_id.isdigit():
                raise serializers.ValidationError({"national_id": "الرقم الوطني يجب أن يكون أرقام فقط"})
            if not (11 <= len(national_id) <= 15):
                raise serializers.ValidationError({"national_id": "الرقم الوطني يجب أن يكون بين 11 و15 رقم"})
        else:
            raise serializers.ValidationError({"national_id": "الرقم الوطني مطلوب"})

        return data

    def create(self, validated_data):

        validated_data.pop('password2')
        random_code = ''.join(random.choices('0123456789', k=10))

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'patient'),
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            national_id=validated_data.get('national_id'),
            random_code=random_code,  # ← حفظ الكود
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'role', 'gender',
            'birth_date', 'phone', 'created_at', 'last_login',"random_code"
            , 'national_id'
        ]
        read_only_fields = ['id', 'created_at', 'last_login',"random_code"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)