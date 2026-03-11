
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="تأكيد كلمة المرور")

    class Meta:
        model = CustomUser
        fields = [
            'email', 'name', 'password', 'password2',
            'role', 'gender', 'birth_date', 'phone'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "كلمتا المرور غير متطابقتين"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'patient'),
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'role', 'gender',
            'birth_date', 'phone', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)