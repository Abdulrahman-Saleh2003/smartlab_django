# doctor_notes/serializers.py

from rest_framework import serializers
from .models import DoctorNote
from doctors.serializers import DoctorSerializer
from patients.serializers import PatientSerializer
from reports.serializers import LabReportsSerializer


class DoctorNoteSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    report = LabReportsSerializer(read_only=True, allow_null=True)

    class Meta:
        model = DoctorNote
        fields = [
            'note_id',
            'doctor',
            'patient',
            'report',
            'note_text',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['note_id', 'created_at', 'updated_at', 'doctor']

    def create(self, validated_data):
        # الطبيب الحالي هو اللي بيكتب
        request = self.context['request']
        doctor = request.user.doctor_profile  # بافتراض إن الـ profile موجود
        validated_data['doctor'] = doctor
        return super().create(validated_data)

    def validate_note_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("نص الملاحظة لا يمكن أن يكون فارغًا")
        return value.strip()