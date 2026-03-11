# ai_analysis/serializers.py

from rest_framework import serializers
from .models import AIAnalysis
from patients.serializers import PatientSerializer
from reports.serializers import LabReportsSerializer


class AIAnalysisSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    report = LabReportsSerializer(read_only=True, allow_null=True)

    class Meta:
        model = AIAnalysis
        fields = [
            'analysis_id',
            'patient',
            'report',
            'prediction',
            'confidence',
            'model_version',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['analysis_id', 'created_at', 'updated_at']