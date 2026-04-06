# health_alerts/serializers.py

from rest_framework import serializers
from .models import HealthAlert
from patients.serializers import PatientSerializer
from ai_analysis.serializers import AIAnalysisSerializer


class HealthAlertSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    result = AIAnalysisSerializer(read_only=True, allow_null=True)

    class Meta:
        model = HealthAlert
        fields = [
            'alert_id',
            'patient',
            'result',
            'alert_type',
            'message',
            'is_read',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['alert_id', 'created_at', 'updated_at']