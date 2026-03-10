from rest_framework import serializers
from .models import CustomUser, UserActivityLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'name', 'role', 'gender',
            'birth_date', 'phone', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'password', 'role', 'gender', 'birth_date', 'phone']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role=validated_data.get('role', 'patient'),
            gender=validated_data.get('gender'),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone'),
        )
        return user


class UserActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # أو PrimaryKeyRelatedField إذا بدك UUID فقط

    class Meta:
        model = UserActivityLog
        fields = ['log_id', 'user', 'action', 'created_at']
        read_only_fields = ['log_id', 'created_at']